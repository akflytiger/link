import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import os
def get_proxy():
    """手动构建代理配置"""
    # 从环境变量读取
    proxy_user = os.environ.get('PROXY_USER', 'akflytiger')
    proxy_pass = os.environ.get('PROXY_PASS', '369369369')
    proxy_host = os.environ.get('PROXY_HOST', 'akflytiger.i234.me')
    proxy_port = os.environ.get('PROXY_PORT', '7893')
    
    # 检查是否有缺失
    if not all([proxy_user, proxy_pass, proxy_host, proxy_port]):
        missing = []
        if not proxy_user: missing.append('PROXY_USER')
        if not proxy_pass: missing.append('PROXY_PASS')
        if not proxy_host: missing.append('PROXY_HOST')
        if not proxy_port: missing.append('PROXY_PORT')
        print(f"警告: 缺少以下环境变量: {missing}")
        return None
    
    # 手动构建代理 URL（确保所有值都是字符串）
    proxy_url = f"http://{str(proxy_user)}:{str(proxy_pass)}@{str(proxy_host)}:{str(proxy_port)}"
    
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    print(f"代理已配置: http://{proxy_user}:****@{proxy_host}:{proxy_port}")
    return proxies
proxies=get_proxy()  
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
    }
# 第一步：从GitHub issues页面获取token
github_url = "https://github.com/wzdnzd/aggregator/issues/91"
response = requests.get(github_url,headers=headers,proxies=proxies)
html_content = response.text
baseurl="https://akflytiger.i234.me:25501/sub?target=clash&udp=true&emoji=true&include=%E9%A6%99%E6%B8%AF%7C%E6%97%A5%E6%9C%AC%7C%E6%96%B0%E5%8A%A0%E5%9D%A1&url="
# 使用BeautifulSoup解析HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 提取code标签中的token
paragraphs = soup.find_all('details')
print (paragraphs[0].get_text())
token = paragraphs[0].get_text().split("钥")[1]
paragraphs2 = soup.find_all('p')
url=paragraphs2[10].get_text().split('?', 1)[0].split('：',1)[1]
print (token)
print (url)

# 第二步：使用url+token构建订阅URL并获取内容
subscribe_url = f'{url}?token={token}&target=clash&list=0'

print("正在获取订阅内容URL:", subscribe_url)

'''
print (urlencode(subscribe_url))

fullurl=baseurl+ urlencode(subscribe_url)
print (fullurl)
'''


# 获取订阅内容
subscribe_response = requests.get(subscribe_url,headers=headers,proxies=proxies)

# 检查请求是否成功
if subscribe_response.status_code == 200:
    # 第三步：将内容保存为clash.yaml文件
    with open('clash-auto-4h.yaml', 'w', encoding='utf-8') as file:
        file.write(subscribe_response.text)
    print("订阅内容已成功保存为clash-auto-4h.yaml文件")
else:
    print(f"获取订阅内容失败，HTTP状态码: {subscribe_response.status_code}")
    print("响应内容:", subscribe_response.text)
