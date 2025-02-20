import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock
from typing import List, Tuple
import requests


class ExtensionManager:
    def __init__(self, base_dir: Path, max_workers: int = 8):
        self.base_dir = base_dir
        self.data_dir = base_dir / "src" / "data"
        self.db_path = self.data_dir / "extensions.db"
        self.max_workers = max_workers
        self.db_lock = Lock()
        self.count_lock = Lock()
        self.success_count = 0
        self.failed_count = 0

    def init_database(self) -> None:
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
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
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_extension_full_name ON extensions(extension_full_name)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_last_updated ON extensions(last_updated)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_display_name ON extensions(display_name)"
            )
            conn.commit()

    def fetch_extension_info(self, publisher_extension: str) -> dict:
        """从 VS Code Marketplace 获取扩展信息"""
        query = {
            "assetTypes": [],
            "filters": [
                {
                    "criteria": [
                        {"filterType": 8, "value": "Microsoft.VisualStudio.Code"},
                        {"filterType": 7, "value": publisher_extension},
                    ],
                    "pageNumber": 1,
                    "pageSize": 2,
                }
            ],
            "flags": 0x1 | 0x4,  # IncludeVersions | IncludeCategoryAndTags
        }

        response = requests.post(
            "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery",
            json=query,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json;api-version=3.0-preview.1",
                "Accept-Encoding": "gzip",
                "User-Agent": "VS Code Build",
            },
        )
        data = response.json()
        if not data["results"] or not data["results"][0]["extensions"]:
            raise Exception("找不到扩展信息")

        extension = data["results"][0]["extensions"][0]
        publisher_name, extension_name = publisher_extension.split(".")
        latest_version = extension["versions"][0]["version"]

        return {
            "extensionId": extension["extensionId"],
            "extensionName": extension["extensionName"],
            "extensionFullName": publisher_extension,
            "displayName": extension["displayName"],
            "shortDescription": extension["shortDescription"],
            "downloadUrl": f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher_name}/vsextensions/{extension_name}/{latest_version}/vspackage",
            "filename": f"{publisher_name}.{extension_name}-{latest_version}.vsix",
            "marketplaceUrl": f"https://marketplace.visualstudio.com/items?itemName={publisher_extension}",
            "categories": extension.get("categories", []),
            "tags": extension.get("tags", []),
            "latest_version": {
                "version": latest_version,
                "lastUpdated": extension["versions"][0]["lastUpdated"],
            },
            "version_history": extension["versions"][:6],
        }

    def process_extension(self, extension_id: str) -> Tuple[str, bool, str]:
        """处理单个扩展"""
        try:
            data = self.fetch_extension_info(extension_id)
            filtered_tags = [tag for tag in data["tags"] if tag.startswith("__")]

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
                json.dumps(filtered_tags),
                data["downloadUrl"],
                data["filename"],
                data["marketplaceUrl"],
            )

            with self.db_lock, sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO extensions (
                        extension_id, extension_name, extension_full_name, display_name,
                        short_description, latest_version, last_updated, version_history,
                        categories, tags, download_url, filename, marketplace_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    insert_data,
                )
                conn.commit()

            with self.count_lock:
                self.success_count += 1
            return data["extensionFullName"], True, None

        except Exception as e:
            with self.count_lock:
                self.failed_count += 1
            return extension_id, False, str(e)

    def process_extensions(self, extensions: List[str]) -> None:
        """批量处理扩展"""
        print(f"开始使用 {self.max_workers} 个线程处理 {len(extensions)} 个扩展...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.process_extension, ext) for ext in extensions
            ]
            for future in futures:
                name, success, error = future.result()
                if success:
                    print(f"已导入：{name}")
                else:
                    print(f"处理失败 {name}: {error}")

    def run(self, input_arg: str) -> None:
        """运行扩展管理器"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.init_database()

        # 读取扩展列表
        if input_arg.endswith(".txt"):
            with open(input_arg, "r", encoding="utf-8") as f:
                extensions = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
        else:
            extensions = [input_arg]

        print(f"开始导入数据到数据库：{self.db_path}")
        self.process_extensions(extensions)

        # 输出统计信息
        print("\n导入完成统计：")
        print(f"成功：{self.success_count} 个")
        print(f"失败：{self.failed_count} 个")

        with sqlite3.connect(self.db_path) as conn:
            total_count = conn.execute("SELECT COUNT(*) FROM extensions").fetchone()[0]
            print(f"数据库中总共有 {total_count} 个扩展")


def main():
    """主函数"""
    import sys

    if len(sys.argv) != 2:
        print("使用方法：")
        print("单个扩展：python extension_manager.py publisher.extension")
        print("批量导入：python extension_manager.py extensions.txt")
        sys.exit(1)

    base_dir = Path(__file__).parent.parent
    manager = ExtensionManager(base_dir)
    manager.run(sys.argv[1])


if __name__ == "__main__":
    main()
