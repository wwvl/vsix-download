import requests
import json
from pathlib import Path
from typing import List

# API 配置
MARKETPLACE_API = (
    "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"
)
API_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json;api-version=3.0-preview.1",
    "Accept-Encoding": "gzip",
    "User-Agent": "VS Code Build",
}


def read_extensions(file_path: Path) -> List[str]:
    """从文件中读取扩展列表"""
    if not file_path.exists():
        raise FileNotFoundError(f"找不到文件：{file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        # 过滤空行和注释行
        return [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]


def fetch_extension_info(publisher_extension: str) -> dict:
    """获取扩展信息"""
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
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{str(e)}")
        return None


def save_response(data: dict, filename: str) -> None:
    """保存响应数据到文件"""
    # 创建 data 目录
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # 保存到 data 目录中
    output_path = data_dir / f"{filename}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"结果已保存到：{output_path}")


def main():
    # 读取扩展列表文件
    extensions_file = Path(__file__).parent / "extensions.txt"
    try:
        extensions = read_extensions(extensions_file)
        print(f"从文件中读取到 {len(extensions)} 个扩展")
    except Exception as e:
        print(f"读取扩展列表失败：{str(e)}")
        return

    # 处理每个扩展
    success_count = 0
    fail_count = 0

    for ext in extensions:
        print(f"\n测试扩展：{ext}")
        response = fetch_extension_info(ext)

        if response:
            print("请求成功！")
            save_response(response, ext.replace(".", "_"))
            success_count += 1
        else:
            print("请求失败！")
            fail_count += 1

    # 打印统计信息
    print(f"\n处理完成！")
    print(f"成功：{success_count} 个")
    print(f"失败：{fail_count} 个")


if __name__ == "__main__":
    main()
