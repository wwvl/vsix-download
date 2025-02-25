import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv
from tqdm import tqdm
import json
import argparse
import requests
from requests.exceptions import RequestException

# 类型定义
ExtensionInfo = Dict[str, Any]
VersionInfo = Dict[str, Any]

# 常量定义
# API 相关配置
# https://github.com/microsoft/vscode/blob/main/src/vs/platform/extensionManagement/common/extensionGalleryService.ts#L1159
MARKETPLACE_API = (
    "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"
)
API_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json;api-version=3.0-preview.1",
    "Accept-Encoding": "gzip",
    "User-Agent": "VS Code Build",
}

# 数据处理配置
MAX_VERSION_HISTORY = 20  # 保留的版本历史数量
MAX_WORKERS = 8  # 并发处理的最大工作线程数
TARGET_PLATFORM = "win32-x64"  # 历史版本中只保留 win32-x64 平台的版本

# 环境变量名
ENV_SUPABASE_URL = "VITE_SUPABASE_URL"
ENV_SUPABASE_KEY = "VITE_SUPABASE_KEY"

# 文件路径
EXTENSIONS_JSON_PATH = "public/data/extensions.json"


class ExtensionError(Exception):
    """扩展处理相关的异常"""

    pass


class ExtensionManager:
    def __init__(self, base_dir: Path):
        """
        初始化扩展管理器

        Args:
            base_dir: 项目根目录
        """
        self.base_dir = base_dir
        self.json_file = self.base_dir / EXTENSIONS_JSON_PATH

        # 初始化数据库连接
        self.supabase = self._init_supabase()

    def _init_supabase(self) -> Client:
        """
        初始化 Supabase 客户端

        Returns:
            Client: Supabase 客户端实例

        Raises:
            FileNotFoundError: .env 文件不存在
            ValueError: 环境变量未设置
        """
        env_path = self.base_dir / ".env"
        if not env_path.exists():
            raise FileNotFoundError(f"找不到.env 文件：{env_path}")

        load_dotenv(env_path)
        url = os.getenv(ENV_SUPABASE_URL)
        key = os.getenv(ENV_SUPABASE_KEY)

        if not url or not key:
            raise ValueError(
                f"请在.env 文件中设置 {ENV_SUPABASE_URL} 和 {ENV_SUPABASE_KEY}"
            )

        return create_client(url, key)

    def _filter_versions(self, versions: List[VersionInfo]) -> List[VersionInfo]:
        """
        过滤版本列表，处理特殊平台版本

        Args:
            versions: 原始版本列表

        Returns:
            List[VersionInfo]: 过滤后的版本列表
        """
        filtered_versions = []
        seen_versions = set()

        for version in versions:
            version_str = version["version"]

            # 检查是否有 targetPlatform 属性
            if "targetPlatform" in version:
                # 只保留指定平台的版本
                if version["targetPlatform"] != TARGET_PLATFORM:
                    continue

            # 避免重复版本
            if version_str not in seen_versions:
                seen_versions.add(version_str)
                filtered_versions.append(version)

        return filtered_versions[:MAX_VERSION_HISTORY]

    def fetch_extension_info(self, publisher_extension: str) -> ExtensionInfo:
        """
        获取扩展信息

        Args:
            publisher_extension: 扩展标识符 (publisher.extension)

        Returns:
            ExtensionInfo: 扩展信息

        Raises:
            ExtensionError: 获取扩展信息失败
            ValueError: 扩展标识符格式错误
        """
        try:
            publisher_name, extension_name = publisher_extension.split(".")
        except ValueError:
            raise ValueError(
                f"扩展标识符格式错误：{publisher_extension}，应为 publisher.extension 格式"
            )

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

        try:
            response = requests.post(MARKETPLACE_API, json=query, headers=API_HEADERS)
            response.raise_for_status()
            data = response.json()
        except RequestException as e:
            raise ExtensionError(f"请求扩展信息失败：{str(e)}")

        if not data["results"] or not data["results"][0]["extensions"]:
            raise ExtensionError(f"找不到扩展信息：{publisher_extension}")

        extension = data["results"][0]["extensions"][0]

        # 过滤并处理版本列表
        filtered_versions = self._filter_versions(extension["versions"])
        latest_version = filtered_versions[0]

        return {
            # "extension_id": extension["extensionId"],
            "extension_name": publisher_extension,
            "display_name": extension["displayName"],
            "short_description": extension["shortDescription"],
            "latest_version": latest_version["version"],
            "last_updated": latest_version["lastUpdated"],
            "version_history": [
                {"version": v["version"], "lastUpdated": v["lastUpdated"]}
                for v in filtered_versions
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
        """
        批量处理扩展信息

        Args:
            extensions: 扩展标识符列表
        """
        print(f"开始处理 {len(extensions)} 个扩展...")

        try:
            # 清理数据库
            self.supabase.table("extensions").delete().filter(
                "extension_name", "neq", ""
            ).execute()

            # 获取扩展信息
            all_data = []
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = [
                    executor.submit(self.fetch_extension_info, ext)
                    for ext in extensions
                ]

                for future in tqdm(futures, desc="获取扩展信息", ncols=66):
                    try:
                        data = future.result()
                        all_data.append(data)
                    except Exception as e:
                        tqdm.write(f"处理失败：{str(e)}")

            # 批量保存数据
            if all_data:
                # 保存到 Supabase
                self.supabase.table("extensions").upsert(all_data).execute()

                # 保存到 JSON 文件
                self.json_file.write_text(
                    json.dumps(all_data, ensure_ascii=False, indent=2), encoding="utf-8"
                )

                print(f"成功处理 {len(all_data)} 个扩展")
            else:
                print("没有成功处理任何扩展")

        except Exception as e:
            print(f"处理过程出错：{str(e)}")

    def run(self, input_path: str) -> None:
        """
        运行扩展管理器

        Args:
            input_path: 扩展名称或包含扩展列表的文本文件路径
        """
        try:
            # 读取扩展列表
            if input_path.endswith(".txt"):
                try:
                    with open(input_path, "r", encoding="utf-8") as f:
                        extensions = [
                            line.strip()
                            for line in f
                            if line.strip() and not line.startswith("#")
                        ]
                except IOError as e:
                    raise ExtensionError(f"读取扩展列表文件失败：{str(e)}")
            else:
                extensions = [input_path]

            if not extensions:
                raise ExtensionError("没有找到要处理的扩展")

            self.process_extensions(extensions)

        except Exception as e:
            print(f"运行失败：{str(e)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="VSCode 扩展管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  %(prog)s publisher.extension          # 处理单个扩展
  %(prog)s extensions.txt               # 批量处理扩展列表
        """,
    )
    parser.add_argument("input", help="扩展名称或包含扩展列表的文本文件")
    args = parser.parse_args()

    try:
        manager = ExtensionManager(Path(__file__).parent.parent)
        manager.run(args.input)
    except KeyboardInterrupt:
        print("\n操作已取消")
    except Exception as e:
        print(f"程序执行出错：{str(e)}")


if __name__ == "__main__":
    main()
