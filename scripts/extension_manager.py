import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Dict
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
from tqdm import tqdm
import json

# 类型定义
ExtensionInfo = Dict[str, any]

# 常量定义
# https://github.com/microsoft/vscode/blob/main/src/vs/platform/extensionManagement/common/extensionGalleryService.ts#L1159
MARKETPLACE_API = (
    "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"
)
MAX_VERSION_HISTORY = 20
API_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json;api-version=3.0-preview.1",
    "Accept-Encoding": "gzip",
    "User-Agent": "VS Code Build",
}


class ExtensionManager:
    def __init__(self, base_dir: Path, max_workers: int = 8):
        self.base_dir = base_dir
        self.max_workers = max_workers
        self.data_dir = self.base_dir / "src" / "data"
        self.json_file = self.data_dir / "extensions.json"
        self.supabase = self._init_supabase()

        # 创建必要的目录
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "extensions").mkdir(parents=True, exist_ok=True)

    def _init_supabase(self) -> Client:
        """初始化 Supabase 客户端"""
        env_path = self.base_dir / ".env"
        if not env_path.exists():
            raise FileNotFoundError(f"找不到.env 文件：{env_path}")

        load_dotenv(env_path)
        url = os.getenv("VITE_SUPABASE_URL")
        key = os.getenv("VITE_SUPABASE_KEY")

        if not url or not key:
            raise ValueError(
                "请在.env 文件中设置 VITE_SUPABASE_URL 和 VITE_SUPABASE_KEY"
            )

        return create_client(url, key)

    def fetch_extension_info(self, publisher_extension: str) -> ExtensionInfo:
        """获取扩展信息"""
        publisher_name, extension_name = publisher_extension.split(".")

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
            "flags": 0x5,
        }

        response = requests.post(MARKETPLACE_API, json=query, headers=API_HEADERS)
        data = response.json()

        if not data["results"] or not data["results"][0]["extensions"]:
            raise ValueError(f"找不到扩展信息：{publisher_extension}")

        extension = data["results"][0]["extensions"][0]
        latest_version = extension["versions"][0]

        return {
            # "extension_id": extension["extensionId"],
            "extension_name": publisher_extension,
            "display_name": extension["displayName"],
            "short_description": extension["shortDescription"],
            "latest_version": latest_version["version"],
            "last_updated": latest_version["lastUpdated"],
            "version_history": [
                {"version": v["version"], "lastUpdated": v["lastUpdated"]}
                for v in extension["versions"][:MAX_VERSION_HISTORY]
            ],
            "categories": extension.get("categories", []),
            "tags": [
                tag for tag in extension.get("tags", []) if not tag.startswith("__")
            ],
            "download_url": f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher_name}/vsextensions/{extension_name}/{latest_version['version']}/vspackage",
            # "filename": f"{publisher_name}.{extension_name}-{latest_version['version']}.vsix",
            "marketplace_url": f"https://marketplace.visualstudio.com/items?itemName={publisher_extension}",
        }

    def process_extensions(self, extensions: List[str]) -> None:
        """批量处理扩展信息"""
        print(f"开始处理 {len(extensions)} 个扩展...")

        # 清理数据库
        self.supabase.table("extensions").delete().filter(
            "extension_name", "neq", ""
        ).execute()

        # 获取扩展信息
        all_data = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.fetch_extension_info, ext) for ext in extensions
            ]

            for future in tqdm(futures, desc="获取扩展信息", ncols=66):
                try:
                    data = future.result()
                    all_data.append(data)

                    # 保存单个扩展信息
                    extension_file = (
                        self.data_dir / "extensions" / f"{data['extension_name']}.json"
                    )
                    with open(extension_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                except Exception as e:
                    tqdm.write(f"处理失败：{str(e)}")

        # 批量保存数据
        if all_data:
            try:
                # 保存到 Supabase
                self.supabase.table("extensions").upsert(all_data).execute()

                # 保存到 JSON 文件
                with open(self.json_file, "w", encoding="utf-8") as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)

                print(f"成功处理 {len(all_data)} 个扩展")
            except Exception as e:
                print(f"保存数据失败：{str(e)}")

    def run(self, input_path: str) -> None:
        """运行扩展管理器"""
        # 读取扩展列表
        if input_path.endswith(".txt"):
            with open(input_path, "r", encoding="utf-8") as f:
                extensions = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
        else:
            extensions = [input_path]

        self.process_extensions(extensions)


def main():
    """主函数"""
    import sys

    if len(sys.argv) != 2:
        print("使用方法：")
        print("单个扩展：python extension_manager.py publisher.extension")
        print("批量导入：python extension_manager.py extensions.txt")
        sys.exit(1)

    manager = ExtensionManager(Path(__file__).parent.parent)
    manager.run(sys.argv[1])


if __name__ == "__main__":
    main()
