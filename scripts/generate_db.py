import os
import json
import sqlite3
from pathlib import Path
import concurrent.futures
import threading
from typing import List, Dict, Any


def filter_tags(tags: List[str]) -> List[str]:
    """过滤标签，保留以 __ 开头的标签

    Args:
        tags: 标签列表

    Returns:
        List[str]: 过滤后的标签列表
    """
    return [tag for tag in tags if tag.startswith("__")]


def init_database(db_path: Path) -> sqlite3.Connection:
    """初始化数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建扩展表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS extensions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        extension_id TEXT NOT NULL UNIQUE,
        extension_name TEXT NOT NULL,
        extension_full_name TEXT NOT NULL UNIQUE,
        display_name TEXT NOT NULL,
        short_description TEXT,
        latest_version TEXT NOT NULL,
        last_updated DATETIME NOT NULL,
        version_history TEXT NOT NULL,
        categories TEXT,
        tags TEXT,
        download_url TEXT NOT NULL,
        filename TEXT NOT NULL,
        marketplace_url TEXT NOT NULL
    )
    """)

    # 创建索引
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_extension_full_name ON extensions(extension_full_name)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_last_updated ON extensions(last_updated)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_display_name ON extensions(display_name)"
    )

    conn.commit()
    return conn


def process_json_file(file_path: Path, db_path: Path, lock: threading.Lock) -> tuple:
    """处理单个 JSON 文件

    Args:
        file_path: JSON 文件路径
        db_path: 数据库文件路径
        lock: 线程锁

    Returns:
        tuple: (文件名，是否成功，错误信息)
    """
    try:
        # 读取 JSON 文件
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 过滤标签
        filtered_tags = filter_tags(data["tags"])

        # 准备插入的数据
        insert_data = (
            data["extensionId"],
            data["extensionName"],
            data["extensionFullName"],
            data["displayName"],
            data["shortDescription"],
            data["latest_version"]["version"],
            data["latest_version"]["lastUpdated"],
            json.dumps(data["version_history"]),
            json.dumps(data["categories"]),
            json.dumps(filtered_tags),  # 使用过滤后的标签
            data["downloadUrl"],
            data["filename"],
            data["marketplaceUrl"],
        )

        # 使用线程锁保护数据库操作
        with lock:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO extensions (
                    extension_id,
                    extension_name,
                    extension_full_name,
                    display_name,
                    short_description,
                    latest_version,
                    last_updated,
                    version_history,
                    categories,
                    tags,
                    download_url,
                    filename,
                    marketplace_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                insert_data,
            )

            conn.commit()
            conn.close()

        return (data["extensionFullName"], True, None)

    except Exception as e:
        return (str(file_path), False, str(e))


def import_json_to_db(json_dir: Path, db_path: Path, max_workers: int = 4):
    """导入 JSON 文件到数据库

    Args:
        json_dir: JSON 文件目录
        db_path: 数据库文件路径
        max_workers: 最大线程数
    """
    # 初始化数据库
    init_database(db_path)

    # 获取所有 JSON 文件
    json_files = list(Path(json_dir).glob("*.json"))

    # 创建线程锁
    db_lock = threading.Lock()

    # 创建线程安全的计数器
    success_count = 0
    failed_count = 0
    count_lock = threading.Lock()

    def update_counts(success: bool):
        nonlocal success_count, failed_count
        with count_lock:
            if success:
                success_count += 1
            else:
                failed_count += 1

    print(f"开始使用 {max_workers} 个线程处理 {len(json_files)} 个文件...")

    # 使用线程池处理文件
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(process_json_file, f, db_path, db_lock): f
            for f in json_files
        }

        for future in concurrent.futures.as_completed(future_to_file):
            file_name, success, error = future.result()
            update_counts(success)

            if success:
                print(f"已导入：{file_name}")
            else:
                print(f"处理失败 {file_name}: {error}")

    return success_count, failed_count


def main():
    """主函数"""
    # 设置路径
    base_dir = Path(__file__).parent.parent
    json_dir = base_dir / "src" / "data"
    db_path = base_dir / "src" / "data" / "extensions.db"

    # 确保目录存在
    json_dir.mkdir(parents=True, exist_ok=True)

    # 设置线程数（可以根据需要调整）
    max_workers = 4

    print(f"开始导入数据到数据库：{db_path}")
    success_count, failed_count = import_json_to_db(json_dir, db_path, max_workers)

    print("\n导入完成统计：")
    print(f"成功：{success_count} 个")
    print(f"失败：{failed_count} 个")

    # 显示最终的数据库统计
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM extensions")
    total_count = cursor.fetchone()[0]
    print(f"数据库中总共有 {total_count} 个扩展")
    conn.close()


if __name__ == "__main__":
    main()
