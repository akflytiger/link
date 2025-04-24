# -*- coding: utf-8 -*-
import requests
import yaml
import os
import sys
import re  # 导入正则表达式模块

# --- 配置 ---
# 要读取的 URL
github_issue_url = "https://github.com/wzdnzd/aggregator/issues/91" # GitHub issue URL
url = "" # 先定义 url，后续会赋值
# 要保留的关键字 (香港 或 日本)
keywords = ["香港", "日本"]
# 输出文件名（仅用于Gist中的文件名）
output_filename = "hk.yaml"

# --- 函数定义 ---

def filter_proxies(data, keywords_to_keep):
    """
    过滤代理列表，只保留名称包含指定关键字的节点。

    Args:
        data (dict): 解析后的 YAML 数据字典。
        keywords_to_keep (list): 要保留的关键字列表。

    Returns:
        dict: 包含过滤后代理列表的数据字典。
              如果原始数据无效或没有 'proxies' 键，则返回 None。
    """
    if not isinstance(data, dict) or 'proxies' not in data or not isinstance(data['proxies'], list):
        print("错误：YAML 数据格式无效或缺少 'proxies' 列表。")
        return None

    filtered_proxies = []
    original_proxies = data.get('proxies', [])

    print(f"开始过滤 {len(original_proxies)} 个代理节点...")

    for proxy in original_proxies:
        # 确保代理是字典并且有 'name' 键
        if isinstance(proxy, dict) and 'name' in proxy:
            proxy_name = proxy.get('name', '')
            # 检查名称是否包含任何一个关键字
            if any(keyword in proxy_name for keyword in keywords_to_keep):
                filtered_proxies.append(proxy)
        else:
            print(f"警告：跳过格式不正确的代理条目：{proxy}")

    print(f"过滤完成，保留了 {len(filtered_proxies)} 个节点。")
    # 用过滤后的列表替换原始列表
    data['proxies'] = filtered_proxies
    return data

def extract_clash_url(github_url):
    """
    从 GitHub issue 页面提取 Clash 订阅 URL。

    Args:
        github_url (str): GitHub issue 的 URL。

    Returns:
        str: 提取到的 Clash 订阅 URL，如果未找到则返回 None。
    """
    try:
        response = requests.get(github_url, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'  # 确保使用 UTF-8 编码
        html_content = response.text
        # 使用正则表达式匹配 "clash订阅" 后面的链接
        match = re.search(r'clash订阅.*?(\bhttps?://\S+)', html_content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()  # 返回匹配到的 URL 并移除空白字符
        else:
            print("警告：在 GitHub issue 中未找到 Clash 订阅 URL。")
            return None
    except requests.exceptions.RequestException as e:
        print(f"错误：从 GitHub issue 下载数据失败: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"错误：提取 Clash 订阅 URL 时发生未知错误: {e}", file=sys.stderr)
        return None

def create_gist(filename, content, token, gist_id=None):
    """
    创建或更新 GitHub Gist。

    Args:
        filename (str): Gist 中的文件名。
        content (str): 文件内容。
        token (str): GitHub 个人访问令牌。
        gist_id (str, 可选): 要更新的 Gist 的 ID。如果为 None，则创建新的 Gist。

    Returns:
        str: Gist 的 URL，如果创建/更新失败则返回 None。
    """
    api_url = f"https://api.github.com/gists"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "files": {
            filename: {
                "content": content
            }
        },
        "public": False  # 创建私有 Gist
    }

    if gist_id:
        # 更新现有的 Gist
        api_url = f"{api_url}/{gist_id}"
        response = requests.patch(api_url, headers=headers, json=payload)
    else:
        # 创建新的 Gist
        response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        return response.json()["html_url"]
    else:
        print(f"错误：创建/更新 Gist 失败，状态码: {response.status_code}, 响应: {response.text}", file=sys.stderr)
        return None

# --- 主程序逻辑 ---

if __name__ == "__main__":
    # 从环境变量中获取 GitHub 令牌和 Gist ID
    github_token = os.environ.get("GIST_PAT")
    gist_id = os.environ.get("GIST_LINK")  # 允许更新现有的 Gist

    if not github_token:
        print("错误：请设置 GITHUB_TOKEN 环境变量。", file=sys.stderr)
        sys.exit(1)

    # 提取 Clash 订阅 URL
    clash_url = extract_clash_url(github_issue_url)
    if clash_url:
        url = clash_url  # 将提取的 URL 赋值给 url 变量
        print(f"从 GitHub issue 提取到 Clash 订阅 URL: {url}")
    else:
        print("错误：无法获取 Clash 订阅 URL。", file=sys.stderr)
        sys.exit(1)

    print(f"正在从 URL 下载数据: {url}")
    try:
        # 发送 GET 请求，设置超时
        response = requests.get(url, timeout=30)
        # 检查请求是否成功
        response.raise_for_status()
        # 显式设置编码为 utf-8 以处理中文
        response.encoding = 'utf-8'
        yaml_content = response.text
        print("数据下载成功。")

    except requests.exceptions.RequestException as e:
        print(f"错误：无法从 URL 下载数据。{e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"下载过程中发生未知错误: {e}", file=sys.stderr)
        sys.exit(1)

    print("正在解析 YAML 数据...")
    try:
        # 使用 safe_load 解析 YAML
        data = yaml.safe_load(yaml_content)
        if data is None:
             print("错误：YAML 内容为空或无效。", file=sys.stderr)
             sys.exit(1)
        print("YAML 解析成功。")

    except yaml.YAMLError as e:
        print(f"错误：无法解析 YAML 数据。{e}", file=sys.stderr)
        print("\n--- YAML 内容片段 (前 500 字符) ---", file=sys.stderr)
        print(yaml_content[:500], file=sys.stderr)
        print("------------------------------------", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"解析过程中发生未知错误: {e}", file=sys.stderr)
        sys.exit(1)

    # 过滤代理
    filtered_data = filter_proxies(data, keywords)
    if not filtered_data:
        print("未能生成过滤后的数据。", file=sys.stderr)
        sys.exit(1)

    # 将YAML数据转换为字符串
    try:
        yaml_content = yaml.dump(filtered_data, allow_unicode=True, sort_keys=False)
    except Exception as e:
        print(f"错误：YAML转换失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 将数据保存到 Gist
    gist_url = create_gist(output_filename, yaml_content, github_token, gist_id)
    if gist_url:
        print(f"数据已成功保存到 Gist: {gist_url}")
    else:
        print("错误：保存数据到 Gist 失败。", file=sys.stderr)
        sys.exit(1)
