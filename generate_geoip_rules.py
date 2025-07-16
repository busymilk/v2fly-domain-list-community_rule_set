

# -*- coding: utf-8 -*-
import os
import sys
import requests
import zipfile
import subprocess
import shutil
import platform

def generate_geoip_rules():
    """
    完整的 GeoIP 规则转换流程。
    1. 下载最新的 geoip.dat 和 V2Ray-Core 工具。
    2. 为指定的国家/地区代码提取 IP CIDR 列表。
    3. 将列表转换为 Clash 的 RULE-SET 格式。
    4. 清理临时文件。
    """
    # --- 配置 ---
    GEOIP_DAT_URL = "https://raw.githubusercontent.com/Loyalsoldier/geoip/release/geoip.dat"
    V2RAY_API_URL = "https://api.github.com/repos/v2fly/v2ray-core/releases/latest"
    # 您可以在这里添加或修改需要生成的国家/地区代码
    COUNTRY_CODES = [
        'cn', 'private', 'cloudflare', 'cloudfront', 'facebook', 
        'fastly', 'google', 'netflix', 'telegram', 'twitter', 'tor'
    ] 
    
    TEMP_DIR = "temp_geoip_gen"
    OUTPUT_DIR = "geoip-rules-generated"
    V2CTL_EXEC_PATH = os.path.join(TEMP_DIR, "v2ctl")
    GEOIP_DAT_PATH = os.path.join(TEMP_DIR, "geoip.dat")

    print("--- 开始生成 GeoIP 规则集 ---")

    # --- 步骤 1: 设置环境和下载文件 ---
    print("步骤 1: 清理并创建临时目录和输出目录...")
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(TEMP_DIR)
    os.makedirs(OUTPUT_DIR)

    try:
        # 下载 geoip.dat
        print(f"正在下载 geoip.dat 从: {GEOIP_DAT_URL}")
        response = requests.get(GEOIP_DAT_URL)
        response.raise_for_status()
        with open(GEOIP_DAT_PATH, 'wb') as f:
            f.write(response.content)
        print("geoip.dat 下载完成。")

        # 下载并解压 V2Ray-Core
        print("正在获取最新的 V2Ray-Core 版本信息...")
        release_info = requests.get(V2RAY_API_URL).json()
        # 根据 GitHub Actions 的运行环境 (Linux) 选择资源
        asset_url = next((asset['browser_download_url'] for asset in release_info['assets'] if 'v2ray-linux-64.zip' in asset['name']), None)
        if not asset_url:
            print("错误: 无法找到适用于 linux-64 的 V2Ray-Core 发布包。")
            sys.exit(1)

        print(f"正在下载 V2Ray-Core 从: {asset_url}")
        zip_path = os.path.join(TEMP_DIR, "v2ray.zip")
        response = requests.get(asset_url)
        response.raise_for_status()
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        print("正在解压 v2ctl 工具...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 从压缩包中只解压出我们需要的 v2ctl 文件
            zip_ref.extract('v2ctl', TEMP_DIR)
        os.chmod(V2CTL_EXEC_PATH, 0o755)
        print("v2ctl 工具准备就绪。")

        # --- 步骤 2: 生成规则 ---
        print("步骤 2: 开始为指定的国家/地区代码生成规则...")
        for code in COUNTRY_CODES:
            print(f"正在处理代码: {code}")
            output_file = os.path.join(OUTPUT_DIR, f"geoip_{code}.txt")
            
            # 使用 v2ctl geoip 命令提取 IP 列表
            # 我们使用下载的最新的 geoip.dat，而不是 v2ray 自带的
            command = [V2CTL_EXEC_PATH, "geoip", f"--dat-path={GEOIP_DAT_PATH}", code]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            ip_list = result.stdout.strip().split('\n')

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("payload:\n")
                for ip_cidr in ip_list:
                    if ip_cidr:
                        f.write(f"  - IP-CIDR,{ip_cidr}\n")
            print(f"已生成规则文件: {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"网络错误: {e}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"执行 v2ctl 命令时出错: {e}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"发生未知错误: {e}")
        sys.exit(1)
    finally:
        # --- 步骤 3: 清理 ---
        print("步骤 3: 清理临时文件...")
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
    
    print("--- GeoIP 规则集生成完毕 ---")

if __name__ == '__main__':
    generate_geoip_rules()
