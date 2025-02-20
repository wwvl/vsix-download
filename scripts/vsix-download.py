import requests
import json
import sys
import os
from enum import Enum
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import threading


# https://github.com/microsoft/vscode/blob/main/src/vs/platform/extensionManagement/common/extensionGalleryService.ts#L1159
class FilterType(Enum):
    """VS Code 扩展查询过滤器类型"""

    ExtensionName = 7
    Target = 8
    ExcludeWithFlags = 12


class Flags(Enum):
    """VS Code 扩展查询过滤器标志位"""

    None_ = 0x0
    IncludeVersions = 0x1
    IncludeFiles = 0x2
    IncludeCategoryAndTags = 0x4
    IncludeSharedAccounts = 0x8
    IncludeVersionProperties = 0x10
    ExcludeNonValidated = 0x20
    IncludeInstallationTargets = 0x40
    IncludeAssetUri = 0x80
    IncludeStatistics = 0x100
    IncludeLatestVersionOnly = 0x200
    Unpublished = 0x1000
    IncludeNameConflictInfo = 0x8000


def get_marketplace_url(publisher_extension):
    """生成扩展的 Marketplace URL

    Args:
        publisher_extension (str): 扩展标识符

    Returns:
        str: Marketplace URL
    """
    return f"https://marketplace.visualstudio.com/items?itemName={publisher_extension}"


def get_extension_info(publisher_extension):
    """获取 VS Code 扩展的完整信息

    Args:
        publisher_extension (str): 扩展的标识符，格式为 'publisher.extension'

    Returns:
        tuple: (基本信息字典，版本信息列表，最新版本信息)
    """
    # 获取扩展基本信息和版本历史
    query = {
        "assetTypes": [],
        "filters": [
            {
                "criteria": [
                    {
                        "filterType": FilterType.Target.value,
                        "value": "Microsoft.VisualStudio.Code",
                    },
                    {
                        "filterType": FilterType.ExtensionName.value,
                        "value": publisher_extension,
                    },
                ],
                "pageNumber": 1,
                "pageSize": 2,
            }
        ],
        "flags": Flags.IncludeVersions.value | Flags.IncludeCategoryAndTags.value,
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json;api-version=3.0-preview.1",
        "Accept-Encoding": "gzip",
        # 'Content-Length': String(data.length),
        "User-Agent": "VS Code Build",
    }

    # 发送请求获取数据
    response = requests.post(
        "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery",
        data=json.dumps(query),
        headers=headers,
    )

    # 解析数据
    # with open("data.json", "w", encoding="utf-8") as f:
    #     f.write(json.dumps(response.json(), indent=2))

    data = response.json()

    # 添加错误处理
    if not data["results"] or not data["results"][0]["extensions"]:
        raise Exception("找不到扩展信息")

    extension = data["results"][0]["extensions"][0]
    latest_version = extension["versions"][0]["version"]

    # 拆分扩展标识符
    publisherName, extensionName = publisher_extension.split(".")

    basic_info = {
        "extensionId": extension["extensionId"],
        "extensionName": extension["extensionName"],
        "displayName": extension["displayName"],
        "shortDescription": extension["shortDescription"],
        "downloadUrl": get_download_url(publisherName, extensionName, latest_version),
        "filename": get_download_filename(publisherName, extensionName, latest_version),
        "categories": extension.get("categories", []),
        "tags": extension.get("tags", []),
        "marketplaceUrl": get_marketplace_url(publisher_extension),
    }
    versions_info = [
        {"version": version["version"], "lastUpdated": version["lastUpdated"]}
        for version in extension["versions"][:6]
    ]

    latest_version_info = versions_info[0] if versions_info else None

    return basic_info, versions_info, latest_version_info


def get_download_url(publisherName, extensionName, version):
    """生成扩展的下载链接

    Args:
        publisherName (str): 发布者名称
        extensionName (str): 扩展名称
        version (str): 扩展版本

    Returns:
        str: 下载链接
    """
    return f"https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisherName}/vsextensions/{extensionName}/{version}/vspackage"


def get_download_filename(publisherName, extensionName, version):
    """生成下载文件名

    Args:
        publisherName (str): 发布者名称
        extensionName (str): 扩展名称
        version (str): 扩展版本

    Returns:
        str: 文件名
    """
    return f"{publisherName}.{extensionName}-{version}.vsix"


def read_extensions_from_file(file_path):
    """从文件中读取扩展列表

    Args:
        file_path (str): 扩展列表文件路径

    Returns:
        list: 扩展列表，每个元素格式为 'publisher.extension'

    Raises:
        FileNotFoundError: 文件不存在时抛出
        Exception: 文件读取错误时抛出
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # 读取所有行，去除空白字符，过滤掉空行和注释行
            extensions = [
                line.strip()
                for line in f.readlines()
                if line.strip() and not line.strip().startswith("#")
            ]
        return extensions
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到文件：{file_path}")
    except Exception as e:
        raise Exception(f"读取文件 {file_path} 时出错：{str(e)}")


def save_extension_info_to_json(
    publisher_extension, basic_info, versions_info, latest_version
):
    """将扩展信息保存到 JSON 文件

    Args:
        publisher_extension (str): 扩展标识符
        basic_info (dict): 基本信息
        versions_info (list): 版本历史信息
        latest_version (dict): 最新版本信息

    Returns:
        str: 保存的文件路径
    """
    # 直接使用 basic_info 作为基础，添加其他信息
    output_data = {
        **basic_info,  # 展开 basic_info 字典
        "latest_version": latest_version,
        "version_history": versions_info,
    }

    # 创建上一层目录的 data 目录
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
    )
    os.makedirs(output_dir, exist_ok=True)

    # 生成输出文件路径
    output_file = os.path.join(output_dir, f"{publisher_extension}.json")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        return output_file
    except Exception as e:
        raise Exception(f"保存 JSON 文件时出错：{str(e)}")


def process_extension(publisher_extension):
    """处理单个扩展的信息

    Args:
        publisher_extension (str): 扩展标识符

    Returns:
        tuple: (publisher_extension, success, error_message)
    """
    try:
        basic_info, versions_info, latest_version = get_extension_info(
            publisher_extension
        )

        save_extension_info_to_json(
            publisher_extension, basic_info, versions_info, latest_version
        )

        return publisher_extension, True, None
    except Exception as e:
        return publisher_extension, False, str(e)


def main():
    """主函数：从命令行获取扩展标识符或文件路径并保存信息到 JSON 文件"""
    if len(sys.argv) < 2:
        print("使用方法：python vsix-download.py [选项] <参数>\n")
        print("选项：")
        print("  -f, --file <file_path>    从文件读取扩展列表")
        print("  -t, --threads <number>     设置线程数（默认为 4）")
        print("  直接输入扩展名称          直接指定一个或多个扩展\n")
        print("示例：")
        print("  python vsix-download.py -f extensions.txt -t 8")
        print("  python vsix-download.py publisher.extension")
        print("  python vsix-download.py pub1.ext1 pub2.ext2")
        print("\n输出：")
        print("  信息将保存在 extension_info 目录下的 JSON 文件中")
        sys.exit(1)

    extensions = []
    max_workers = 4  # 默认线程数

    # 解析命令行参数
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] in ["-f", "--file"]:
            if i + 1 >= len(sys.argv):
                print("错误：使用 -f/--file 选项时必须指定文件路径")
                sys.exit(1)
            try:
                file_path = sys.argv[i + 1]
                extensions = read_extensions_from_file(file_path)
                print(f"从文件 {file_path} 中读取到 {len(extensions)} 个扩展")
                i += 2
            except Exception as e:
                print(f"错误：{str(e)}")
                sys.exit(1)
        elif sys.argv[i] in ["-t", "--threads"]:
            if i + 1 >= len(sys.argv):
                print("错误：使用 -t/--threads 选项时必须指定线程数")
                sys.exit(1)
            try:
                max_workers = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print("错误：线程数必须是整数")
                sys.exit(1)
        else:
            extensions.append(sys.argv[i])
            i += 1

    if not extensions:
        print("错误：没有找到要处理的扩展")
        sys.exit(1)

    success_extensions = []
    failed_extensions = []

    # 使用线程池处理扩展
    print(f"\n使用 {max_workers} 个线程处理 {len(extensions)} 个扩展...")

    # 创建线程安全的列表
    success_lock = threading.Lock()
    failed_lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_extension = {
            executor.submit(process_extension, ext): ext for ext in extensions
        }

        # 处理完成的任务
        for future in concurrent.futures.as_completed(future_to_extension):
            ext, success, error = future.result()
            if success:
                with success_lock:
                    success_extensions.append(ext)
            else:
                with failed_lock:
                    failed_extensions.append((ext, error))

    # 输出处理结果
    total = len(extensions)
    success_count = len(success_extensions)
    failed_count = len(failed_extensions)

    print(
        f"\n处理统计：总计 {total} 个，成功 {success_count} 个，失败 {failed_count} 个"
    )

    if success_extensions:
        print("\n成功处理的扩展：")
        for ext in sorted(success_extensions):  # 排序以保持稳定的输出顺序
            print(f"  - {ext}")

    if failed_extensions:
        print("\n处理失败的扩展：")
        for ext, error in sorted(failed_extensions):  # 排序以保持稳定的输出顺序
            print(f"  - {ext}: {error}")


if __name__ == "__main__":
    main()
