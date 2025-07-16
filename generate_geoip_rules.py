# -*- coding: utf-8 -*-
import os
import sys
import requests
import shutil

def generate_geoip_rules_from_text():
    """
    直接从 Loyalsoldier 的纯文本文件生成 GeoIP 规则集。
    这个方法不再需要 v2ctl 或任何外部二进制文件。
    """
    # --- 配置 ---
    # Loyalsoldier 仓库中纯文本文件的 URL 基础路径
    BASE_URL = "https://raw.githubusercontent.com/Loyalsoldier/geoip/release/text/"
    
    # 需要生成的 GeoIP 类别列表
    GEOIP_CODES = [
        'cn', 'private', 'cloudflare', 'cloudfront', 'facebook', 
        'fastly', 'google', 'netflix', 'telegram', 'twitter', 'tor'
    ]
    
    OUTPUT_DIR = "geoip-rules-generated"

    print("--- 开始从纯文本源生成 GeoIP 规则集 ---")

    # --- 步骤 1: 清理并创建输出目录 ---
    print("步骤 1: 清理并创建输出目录...")
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    # --- 步骤 2: 下载、转换并生成规则 ---
    print("步骤 2: 开始处理每个 GeoIP 类别...")
    for code in GEOIP_CODES:
        url = f"{BASE_URL}{code}.txt"
        output_file = os.path.join(OUTPUT_DIR, f"geoip_{code}.txt")
        
        print(f"正在下载和处理: {code} (来自 {url})")
        
        try:
            response = requests.get(url)
            response.raise_for_status() # 如果下载失败则抛出异常
            ip_list = response.text.strip().split('\n')

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("payload:\n")
                for ip_cidr in ip_list:
                    if ip_cidr and not ip_cidr.startswith('#'):
                        f.write(f"  - IP-CIDR,{ip_cidr}\n")
            print(f"已成功生成规则文件: {output_file}")

        except requests.exceptions.RequestException as e:
            print(f"错误: 下载 {code} 的规则失败: {e}")
            # 选择跳过这个文件而不是中止整个流程
            continue 
        except Exception as e:
            print(f"处理 {code} 时发生未知错误: {e}")
            continue

    print("--- GeoIP 规则集生成完毕 ---")

if __name__ == '__main__':
    generate_geoip_rules_from_text()