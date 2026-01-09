#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OneTab导出文件处理脚本
功能：
1. 合并多个OneTab导出文件（交错合并）
2. 按照类型分类：GitHub、知乎、AI大模型、其他
3. 每30行插入空行用于视觉分隔
4. 保留原有顺序
5. 输出文件添加时间戳前缀，输出到output目录

使用方法:
    python process_onetab.py --input <输入文件夹> [--output <输出文件夹>]

示例:
    python process_onetab.py --input d:\demo-project-onetab
    python process_onetab.py --input d:\demo-project-onetab --output d:\output
"""

import os
import sys
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ==================== 配置区域 ====================
# 输入文件夹（包含OneTab导出的.txt文件）
DEFAULT_INPUT_DIR = r"d:\demo-project-onetab"

# 输出文件夹（默认为输入文件夹下的output子目录）
DEFAULT_OUTPUT_DIR = None  # 如果为None，则使用 input_dir/output

# ===============================================


def read_onetab_file(filepath):
    """读取OneTab文件，返回记录列表（过滤空行）"""
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            # 过滤空行
            if line.strip():
                records.append(line)
    return records


def extract_url(record):
    """从记录中提取URL部分"""
    if "|" in record:
        return record.split("|")[0].strip()
    return record.strip()


def merge_onetab_files(file_paths):
    """交错合并多个OneTab文件"""
    # 读取所有文件的记录
    all_records = []
    for filepath in file_paths:
        records = read_onetab_file(filepath)
        all_records.append(records)

    # 交错合并
    merged = []
    max_length = max(len(records) for records in all_records) if all_records else 0

    for i in range(max_length):
        for records in all_records:
            if i < len(records):
                merged.append(records[i])

    return merged


def deduplicate_records(records):
    """
    去除重复的URL记录，只保留最新的（合并后越靠前的越新）
    """
    seen_urls = set()
    deduplicated = []

    for record in records:
        url = extract_url(record)
        if url not in seen_urls:
            seen_urls.add(url)
            deduplicated.append(record)

    return deduplicated


def classify_record(record):
    """
    分类单条记录
    返回值：'github', 'zhihu', 'ai', 'other'
    """
    url = record.split("|")[0].lower() if "|" in record else record.lower()

    if "github" in url:
        return "github"
    elif "zhihu" in url:
        return "zhihu"
    elif "chatgpt" in url or "claude" in url or "gemini" in url:
        return "ai"
    else:
        return "other"


def add_visual_separators(records):
    """
    每30行插入一个空行作为视觉分隔
    """
    result = []
    for i, record in enumerate(records):
        result.append(record)
        # 每30行后插入空行（但最后一条记录后不插入）
        if (i + 1) % 30 == 0 and i + 1 < len(records):
            result.append("")
    return result


def write_output_file(filepath, records):
    """写入输出文件"""
    with open(filepath, "w", encoding="utf-8") as f:
        for record in records:
            f.write(record + "\n")


def process_onetab_files(input_dir, output_dir=None):
    """主处理函数"""
    # 验证输入目录
    if not os.path.isdir(input_dir):
        print(f"错误: 输入目录不存在 - {input_dir}")
        return

    # 设置输出目录
    if output_dir is None:
        output_dir = os.path.join(input_dir, "output")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 获取当前时间戳（精确到分钟）
    time_prefix = datetime.now().strftime("%Y-%m-%d_%H-%M")

    # 获取所有.txt文件（OneTab导出文件）
    input_files = [str(f) for f in Path(input_dir).glob("*.txt") if f.is_file()]

    if not input_files:
        print("未找到任何.txt文件")
        return

    print(f"找到输入文件: {input_files}")

    # 排序以保证一致性
    input_files.sort()

    # 合并所有文件
    merged_records = merge_onetab_files(input_files)
    print(f"合并后总记录数: {len(merged_records)}")

    # 去除重复记录
    deduplicated_records = deduplicate_records(merged_records)
    print(f"去重后记录数: {len(deduplicated_records)}")
    print(f"删除了{len(merged_records) - len(deduplicated_records)}条重复记录\n")

    # 分类
    classified = defaultdict(list)
    for record in deduplicated_records:
        category = classify_record(record)
        classified[category].append(record)

    # 输出统计
    print("\n分类统计:")
    for category in ["github", "zhihu", "ai", "other"]:
        count = len(classified[category])
        print(f"  {category}: {count}条")

    # 生成输出文件
    output_configs = {
        "github": f"{time_prefix}_github.txt",
        "zhihu": f"{time_prefix}_zhihu.txt",
        "ai": f"{time_prefix}_ai.txt",
        "other": f"{time_prefix}_other.txt",
    }

    for category, filename in output_configs.items():
        if classified[category]:
            records_with_separators = add_visual_separators(classified[category])
            output_path = os.path.join(output_dir, filename)
            write_output_file(output_path, records_with_separators)
            print(f"✓ 生成文件: {filename}")

    print(f"\n处理完成！输出目录: {output_dir}")


if __name__ == "__main__":
    # 使用 argparse 处理命令行参数
    parser = argparse.ArgumentParser(
        description="OneTab导出文件处理脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python process_onetab.py --input d:\\demo-project-onetab
  python process_onetab.py --input d:\\demo-project-onetab --output d:\\output
        """,
    )

    parser.add_argument(
        "--input",
        type=str,
        default=DEFAULT_INPUT_DIR,
        help=f"输入文件夹路径（包含OneTab导出的.txt文件），默认: {DEFAULT_INPUT_DIR}",
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="输出文件夹路径，默认: <输入文件夹>/output",
    )

    args = parser.parse_args()

    input_dir = args.input
    output_dir = args.output if args.output else os.path.join(input_dir, "output")

    process_onetab_files(input_dir, output_dir)
