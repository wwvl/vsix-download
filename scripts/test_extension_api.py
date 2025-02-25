import requests
import json
from pathlib import Path

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
    # 测试的扩展列表
    extensions = ["Continue.continue", "rust-lang.rust-analyzer"]

    for ext in extensions:
        print(f"\n测试扩展：{ext}")
        response = fetch_extension_info(ext)

        if response:
            print("请求成功！")
            save_response(response, ext.replace(".", "_"))
        else:
            print("请求失败！")


if __name__ == "__main__":
    main()
