#!/usr/bin/env python3
import os
from collections import Counter


def remove_duplicates():
    # 获取脚本所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建 extensions.txt 的绝对路径
    file_path = os.path.join(script_dir, "extensions.txt")

    # 读取文件内容
    with open(file_path, "r") as file:
        extensions = file.read().splitlines()

    # 打印原始扩展数量
    print(f"原始扩展数量：{len(extensions)}")

    # 使用 Counter 统计每个 ID 的出现次数
    extension_counts = Counter(extensions)

    # 找出重复的 ID
    duplicates = {ext: count for ext, count in extension_counts.items() if count > 1}

    if duplicates:
        print("\n重复的扩展 ID:")
        for ext, count in duplicates.items():
            print(f"- {ext} (重复 {count - 1} 次)")

    # 使用集合去重
    unique_extensions = set(extensions)

    # 按照不区分首字母大小写的方式排序
    sorted_extensions = sorted(unique_extensions, key=str.lower)

    # 打印去重后的扩展数量
    print(f"\n去重后扩展数量：{len(sorted_extensions)}")
    print(f"移除了 {len(extensions) - len(sorted_extensions)} 个重复项")

    # 将去重并排序后的内容写回文件
    with open(file_path, "w") as file:
        file.write("\n".join(sorted_extensions))

    print(f"已成功将去重并排序后的扩展 ID 写回 {file_path}")


if __name__ == "__main__":
    remove_duplicates()
