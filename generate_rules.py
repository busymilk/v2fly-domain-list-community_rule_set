# -*- coding: utf-8 -*-
import os
import re
import shutil

def convert_and_process_rules():
    """
    完整的规则转换和处理流程（重构版）。
    1. 克隆最新的上游规则仓库。
    2. 在转换 dat 文件时，直接分离域名和标签，确保写入的规则文件是干净的，同时收集标签。
    3. 根据收集到的标签生成聚合规则文件。
    """
    # --- 配置 ---
    source_repo = 'https://github.com/v2fly/domain-list-community.git'
    source_dir_temp = 'domain-list-community-temp'
    source_data_dir = os.path.join(source_dir_temp, 'data')
    output_dir = 'clash-rules-generated'
    collected_tags = {}

    print("步骤 1: 清理旧目录并克隆最新的上游规则...")
    if os.path.exists(source_dir_temp):
        shutil.rmtree(source_dir_temp)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    os.system(f"git clone --depth 1 {source_repo} {source_dir_temp}")
    print("克隆完成。")

    print("步骤 2: 开始转换规则文件并处理标签...")

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
                rules.append(line)
        return rules

    # 遍历源数据目录中的所有文件
    for filename in os.listdir(source_data_dir):
        source_filepath = os.path.join(source_data_dir, filename)
        if not os.path.isfile(source_filepath):
            continue

        processed_files = set()
        all_rules_with_tags = process_file(source_filepath, processed_files, source_data_dir)
        unique_rules = sorted(list(set(all_rules_with_tags)))

        if not unique_rules:
            continue

        output_filepath = os.path.join(output_dir, f"{filename}.txt")
        with open(output_filepath, 'w', encoding='utf-8') as f_out:
            f_out.write('payload:\n')
            for raw_rule in unique_rules:
                # 分离规则和标签
                parts = raw_rule.split(' ')
                rule_content = parts[0]
                tag = None
                if len(parts) > 1 and parts[-1].startswith('@'):
                    tag = parts[-1][1:]

                # 格式化规则
                if rule_content.startswith('regexp:'):
                    # 使用 YAML 字面量块来处理正则表达式，更稳健
                    formatted_rule = f"  - |\n    {rule_content.split(':', 1)[1].strip()}"
                elif rule_content.startswith('full:'):
                    formatted_rule = f"  - 'DOMAIN,{rule_content.split(':', 1)[1].strip()}'"
                elif rule_content.startswith('domain:'):
                    formatted_rule = f"  - 'DOMAIN-SUFFIX,{rule_content.split(':', 1)[1].strip()}'"
                else:
                    formatted_rule = f"  - 'DOMAIN-SUFFIX,{rule_content}'"
                
                # 写入干净的规则到文件
                f_out.write(f"{formatted_rule}\n")

                # 如果有标签，则收集
                if tag:
                    if tag not in collected_tags:
                        collected_tags[tag] = set()
                    collected_tags[tag].add(formatted_rule.strip()) # 添加已格式化的规则

    print("规则文件转换完成，标签已在过程中分离。")

    # --- Part 2: 生成收集到的标签文件 ---
    print("步骤 3: 生成聚合标签规则文件...")
    for tag, rules in collected_tags.items():
        collect_filename = os.path.join(output_dir, f"collect_tag_{tag}.txt")
        with open(collect_filename, 'w', encoding='utf-8') as f_collect:
            f_collect.write('payload:\n')
            for rule in sorted(list(rules)):
                f_collect.write(f"{rule}\n")
        print(f"已生成: {collect_filename}")

    # --- Part 3: 清理 ---
    print("步骤 4: 清理临时文件...")
    if os.path.exists(source_dir_temp):
        shutil.rmtree(source_dir_temp)
    print("所有任务完成！")

if __name__ == '__main__':
    convert_and_process_rules()