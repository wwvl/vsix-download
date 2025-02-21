import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock
from typing import List, Tuple
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
from tqdm import tqdm
import json


class ExtensionManager:
    def __init__(self, base_dir: Path, max_workers: int = 8):
        self.base_dir = base_dir
        self.max_workers = max_workers
        self.count_lock = Lock()
        self.success_count = 0
        self.failed_count = 0

        # 加载 .env 文件
        env_path = self.base_dir / ".env"
        if not env_path.exists():
            raise ValueError(f"找不到 .env 文件：{env_path}")
        load_dotenv(env_path)

        # 初始化 Supabase 客户端
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("请在 .env 文件中设置 SUPABASE_URL 和 SUPABASE_KEY")
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def init_database(self) -> None:
        """初始化数据库：清理旧数据"""
        print("开始清理数据库...")

        try:
            # 删除所有现有数据
            self.supabase.table("extensions").delete().neq("id", 0).execute()
            print("数据清理完成")

        except Exception as e:
            print(f"数据库清理失败：{str(e)}")
            raise

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
            "extension_id": extension["extensionId"],
            "extension_name": extension["extensionName"],
            "extension_full_name": publisher_extension,
            "display_name": extension["displayName"],
            "short_description": extension["shortDescription"],
            "latest_version": latest_version,
            "last_updated": extension["versions"][0]["lastUpdated"],
            "version_history": extension["versions"][:6],
            "categories": extension.get("categories", []),
            "tags": [
                tag for tag in extension.get("tags", []) if not tag.startswith("__")
            ],
            "download_url": f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher_name}/vsextensions/{extension_name}/{latest_version}/vspackage",
            "filename": f"{publisher_name}.{extension_name}-{latest_version}.vsix",
            "marketplace_url": f"https://marketplace.visualstudio.com/items?itemName={publisher_extension}",
        }

    def process_extension(self, extension_id: str) -> Tuple[str, bool, str]:
        """处理单个扩展"""
        try:
            data = self.fetch_extension_info(extension_id)

            # 使用 Supabase 插入数据
            # 注意：search_vector_zh 和 search_vector_en 会通过数据库触发器自动更新
            self.supabase.table("extensions").upsert(
                {
                    "extension_id": data["extension_id"],
                    "extension_name": data["extension_name"],
                    "extension_full_name": data["extension_full_name"],
                    "display_name": data["display_name"],
                    "short_description": data["short_description"],
                    "latest_version": data["latest_version"],
                    "last_updated": data["last_updated"],
                    "version_history": data["version_history"],
                    "categories": data["categories"],
                    "tags": data["tags"],
                    "download_url": data["download_url"],
                    "filename": data["filename"],
                    "marketplace_url": data["marketplace_url"],
                }
            ).execute()

            with self.count_lock:
                self.success_count += 1
            return data["extension_full_name"], True, None

        except Exception as e:
            with self.count_lock:
                self.failed_count += 1
            return extension_id, False, str(e)

    def process_extensions(self, extensions: List[str]) -> None:
        """批量处理扩展"""
        # 1. 先收集所有数据
        all_data = []

        # 确保数据目录存在
        data_dir = self.base_dir / "src" / "data" / "extensions"
        data_dir.mkdir(parents=True, exist_ok=True)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 只获取数据，不插入
            futures = [
                executor.submit(self.fetch_extension_info, ext) for ext in extensions
            ]
            # 使用 tqdm 显示进度，设置最大宽度为 80 列
            for future in tqdm(
                futures, desc="获取扩展信息", total=len(extensions), ncols=66
            ):
                try:
                    data = future.result()
                    all_data.append(data)

                    # 保存扩展信息到文件
                    extension_file = data_dir / f"{data['extension_full_name']}.json"
                    with open(extension_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                except Exception as e:
                    tqdm.write(f"获取失败：{str(e)}")

        # 2. 批量插入
        if all_data:
            print("\n开始导入数据...")
            try:
                self.supabase.table("extensions").upsert(all_data).execute()
                print("导入完成")
            except Exception as e:
                print(f"导入失败：{str(e)}")

    def run(self, input_arg: str) -> None:
        """运行扩展管理器"""
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

        print(f"发现 {len(extensions)} 个扩展，开始处理...")

        # 1. 先清理数据库
        print("\n准备导入数据到 Supabase")
        print("开始清理数据库...")
        self.init_database()

        # 2. 获取和导入数据
        self.process_extensions(extensions)


def main():
    """主函数"""
    import sys

    if len(sys.argv) != 2:
        print("使用方法：")
        print("单个扩展：python extension_manager.py publisher.extension")
        print("批量导入：python extension_manager.py extensions.txt")
        sys.exit(1)

    root_dir = Path(__file__).parent.parent  # 使用相同的根目录路径
    manager = ExtensionManager(root_dir)
    manager.run(sys.argv[1])


if __name__ == "__main__":
    main()
