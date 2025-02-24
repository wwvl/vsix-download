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
        supabase_url = os.getenv("VITE_SUPABASE_URL")
        supabase_key = os.getenv("VITE_SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError(
                "请在 .env 文件中设置 VITE_SUPABASE_URL 和 VITE_SUPABASE_KEY"
            )
        self.supabase: Client = create_client(supabase_url, supabase_key)

        # 确保数据目录存在
        self.data_dir = self.base_dir / "src" / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.json_file = self.data_dir / "extensions.json"

    def init_database(self) -> None:
        """初始化数据库：清理旧数据"""
        print("开始清理数据库...")

        try:
            # 删除所有现有数据，添加一个始终为真的条件以满足 PostgREST 要求
            self.supabase.table("extensions").delete().filter(
                "extension_name", "neq", ""
            ).execute()
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

        # 清理版本历史数据
        cleaned_versions = [
            {
                "version": version.get("version"),
                "lastUpdated": version.get("lastUpdated"),
            }
            for version in extension["versions"][:20]  # 只保留前 20 个版本
        ]

        return {
            # "extension_id": extension["extensionId"],
            "extension_name": publisher_extension,
            "display_name": extension["displayName"],
            "short_description": extension["shortDescription"],
            "latest_version": latest_version,
            "last_updated": extension["versions"][0]["lastUpdated"],
            "version_history": cleaned_versions,
            "categories": extension.get("categories", []),
            "tags": [
                tag for tag in extension.get("tags", []) if not tag.startswith("__")
            ],
            "download_url": f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher_name}/vsextensions/{extension_name}/{latest_version}/vspackage",
            # "filename": f"{publisher_name}.{extension_name}-{latest_version}.vsix",
            "marketplace_url": f"https://marketplace.visualstudio.com/items?itemName={publisher_extension}",
        }

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
                    extension_file = data_dir / f"{data['extension_name']}.json"
                    with open(extension_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                except Exception as e:
                    tqdm.write(f"获取失败：{str(e)}")

        # 2. 批量插入
        if all_data:
            print("\n开始导入数据...")
            try:
                # 保存到 Supabase
                self.supabase.table("extensions").upsert(all_data).execute()
                print("Supabase 导入完成")

                # 保存到 JSON 文件
                print("正在保存到 JSON 文件...")
                with open(self.json_file, "w", encoding="utf-8") as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)
                print(f"JSON 文件保存完成：{self.json_file}")

            except Exception as e:
                print(f"导入失败：{str(e)}")

    def save_to_json(self, data: List[dict]) -> None:
        """保存数据到 JSON 文件"""
        try:
            # 确保数据目录存在
            self.data_dir.mkdir(parents=True, exist_ok=True)

            # 保存数据到 JSON 文件
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存 JSON 文件失败：{str(e)}")
            raise

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
