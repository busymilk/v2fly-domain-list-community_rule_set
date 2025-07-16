

# -*- coding: utf-8 -*-
import os
import re
import shutil

def convert_and_process_rules():
    """
    完整的规则转换和处理流程。
    1. 克隆最新的上游规则仓库。
    2. 将 dat 文件转换为 Clash 规则集格式。
    3. 处理 include 标签。
    4. 收集带 @ 标签的规则并生成单独的文件。
    5. 从所有原始规则文件中移除 @ 标签。
    """
    # --- Part 1: 克隆和转换 ---
    source_repo = 'https://github.com/v2fly/domain-list-community.git'
    source_dir_temp = 'domain-list-community-temp'
    source_data_dir = os.path.join(source_dir_temp, 'data')
    output_dir = 'clash-rules-generated'

    print("步骤 1: 清理旧目录并克隆最新的上游规则...")
    # 清理旧的临时目录和输出目录
    if os.path.exists(source_dir_temp):
        shutil.rmtree(source_dir_temp)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # 克隆最新的规则
    os.system(f"git clone --depth 1 {source_repo} {source_dir_temp}")
    print("克隆完成。")

    print("步骤 2: 开始转换规则文件...")

    # 递归处理 include 的函数
    def process_file(filepath, processed_files, base_dir):
        if filepath in processed_files:
            return []
        processed_files.add(filepath)

        rules = []
        if not os.path.exists(filepath):
            print(f"警告: include 文件未找到: {filepath}")
            return []

        with open(filepath, 'r', encoding='utf-8') as f_in:
            lines = f_in.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.startswith('include:'):
                include_filename = line.split(':', 1)[1].strip()
                include_filepath = os.path.join(base_dir, include_filename)
                rules.extend(process_file(include_filepath, processed_files, base_dir))
            else:
                # 保持原始行的格式，包括可能的标签
                rules.append(line)
        return rules

    # 遍历源数据目录中的所有文件
    for filename in os.listdir(source_data_dir):
        source_filepath = os.path.join(source_data_dir, filename)
        if os.path.isfile(source_filepath):
            processed_files = set()
            all_rules = process_file(source_filepath, processed_files, source_data_dir)
            
            unique_rules = sorted(list(set(all_rules)))

            if unique_rules:
                output_filepath = os.path.join(output_dir, f"{filename}.txt")
                with open(output_filepath, 'w', encoding='utf-8') as f_out:
                    f_out.write('payload:\n')
                    for rule in unique_rules:
                        # 根据 geosite 格式转换为 clash 格式
                        if rule.startswith('regexp:'):
                            f_out.write(f"  - '{rule.split(':', 1)[1].strip()}'\n")
                        elif rule.startswith('full:'):
                            f_out.write(f"  - 'DOMAIN,{rule.split(':', 1)[1].strip()}'\n")
                        elif rule.startswith('domain:'):
                             f_out.write(f"  - 'DOMAIN-SUFFIX,{rule.split(':', 1)[1].strip()}'\n")
                        else:
                            # 默认作为 domain-suffix
                            f_out.write(f"  - 'DOMAIN-SUFFIX,{rule}'\n")
    
    print("规则文件转换完成。")

    # --- Part 2: 标签处理 ---
    print("步骤 3: 开始处理 @ 标签...")
    collected_tags = {}
    tag_pattern = re.compile(r"(@\w+)$") # 匹配行尾的标签

    target_files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]

    for filename in target_files:
        filepath = os.path.join(output_dir, filename)
        cleaned_lines = []
        has_changes = False

        with open(filepath, 'r', encoding='utf-8') as f_in:
            lines = f_in.readlines()

        for line in lines:
            match = tag_pattern.search(line)
            if match:
                has_changes = True
                tag = match.group(1)[1:]  # 提取标签名 (去掉@)
                clean_line = line[:match.start()].strip() # 获取规则部分

                if tag not in collected_tags:
                    collected_tags[tag] = set()
                collected_tags[tag].add(clean_line)
                cleaned_lines.append(f"{clean_line}\n")
            else:
                cleaned_lines.append(line)

        if has_changes:
            with open(filepath, 'w', encoding='utf-8') as f_out:
                f_out.writelines(cleaned_lines)

    print(f"标签收集完成，共找到 {len(collected_tags)} 个标签。")

    # --- Part 3: 生成收集到的标签文件 ---
    print("步骤 4: 生成聚合标签规则文件...")
    for tag, rules in collected_tags.items():
        collect_filename = os.path.join(output_dir, f"collect_tag_{tag}.txt")
        with open(collect_filename, 'w', encoding='utf-8') as f_collect:
            f_collect.write('payload:\n')
            for rule in sorted(list(rules)):
                f_collect.write(f"{rule}\n")
        print(f"已生成: {collect_filename}")

    # --- Part 4: 清理 ---
    print("步骤 5: 清理临时文件...")
    if os.path.exists(source_dir_temp):
        shutil.rmtree(source_dir_temp)
    print("所有任务完成！")

if __name__ == '__main__':
    convert_and_process_rules()
