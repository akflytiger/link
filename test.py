import requests
import yaml

# API URL
url = "https://woyooo-distribute.hf.space/api/v1/subscribe?token=e9ldidvac1nkw4rm&target=clash&list=0"

# 发起请求获取 YAML 内容
response = requests.get(url)
response.raise_for_status()  # 检查请求是否成功

# 解析 YAML 内容
data = yaml.safe_load(response.text)

# 筛选 proxies 中包含 "香港"、"日本" 或 "新加坡" 的节点
filtered_proxies = [
    proxy for proxy in data.get('proxies', [])
    if any(keyword in proxy.get('name', '') for keyword in ['香港', '日本', '新加坡'])
]

# 更新 proxies 字段
data['proxies'] = filtered_proxies

# 保存到 clash-api.yaml 文件
with open('clash-api.yaml', 'w', encoding='utf-8') as f:
    yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

print("已生成 clash-api.yaml 文件")
