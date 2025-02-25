import requests
import argparse
from pathlib import Path
from typing import List, Dict


class VSCodeExtensionDownloader:
    def __init__(self):
        self.marketplace_api = (
            "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"
        )
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json;api-version=3.0-preview.1",
            "User-Agent": "VS Code Build",
        }

    def get_download_url(self, extension_id: str) -> Dict[str, str]:
        """获取扩展的下载信息"""
        publisher_name, extension_name = extension_id.split(".")

        query = {
            "filters": [
                {"criteria": [{"filterType": 7, "value": extension_id}], "pageSize": 1}
            ],
            "flags": 0x5,
        }

        response = requests.post(self.marketplace_api, json=query, headers=self.headers)
        response.raise_for_status()
        data = response.json()

        if not data["results"] or not data["results"][0]["extensions"]:
            raise ValueError(f"找不到扩展：{extension_id}")

        extension = data["results"][0]["extensions"][0]
        latest_version = extension["versions"][0]["version"]

        return {
            "url": f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher_name}/vsextensions/{extension_name}/{latest_version}/vspackage",
            "filename": f"{extension_id}-{latest_version}.vsix",
        }

    def download_extension(self, extension_id: str, save_dir: Path) -> None:
        """下载单个扩展"""
        try:
            info = self.get_download_url(extension_id)
            save_path = save_dir / info["filename"]

            if save_path.exists():
                print(f"扩展已存在：{info['filename']}")
                return

            print(f"正在下载：{info['filename']}")
            response = requests.get(info["url"])
            response.raise_for_status()

            save_path.write_bytes(response.content)
            print(f"下载完成：{info['filename']}")

        except Exception as e:
            print(f"下载失败 {extension_id}: {str(e)}")

    def process_extensions(self, extensions: List[str], save_dir: Path) -> None:
        """处理扩展下载"""
        save_dir.mkdir(parents=True, exist_ok=True)

        for extension in extensions:
            self.download_extension(extension, save_dir)


def main():
    parser = argparse.ArgumentParser(description="VSCode 扩展下载器")
    parser.add_argument("input", help="扩展名称或包含扩展列表的文本文件")
    args = parser.parse_args()

    # 设置下载目录
    save_dir = Path("extensions")

    # 读取扩展列表
    if args.input.endswith(".txt"):
        with open(args.input, "r", encoding="utf-8") as f:
            extensions = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    else:
        extensions = [args.input]

    # 开始下载
    downloader = VSCodeExtensionDownloader()
    downloader.process_extensions(extensions, save_dir)


if __name__ == "__main__":
    main()
