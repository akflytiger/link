import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

# 第一步：从GitHub issues页面获取token
github_url = "https://github.com/wzdnzd/aggregator/issues/91"
response = requests.get(github_url)
html_content = response.text
baseurl="https://akflytiger.i234.me:25501/sub?target=clash&udp=true&emoji=true&include=%E9%A6%99%E6%B8%AF%7C%E6%97%A5%E6%9C%AC%7C%E6%96%B0%E5%8A%A0%E5%9D%A1&url="
# 使用BeautifulSoup解析HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 提取code标签中的token
paragraphs = soup.find_all('code')
print (paragraphs[0].get_text())
token = paragraphs[0].get_text()


# 第二步：使用token构建订阅URL并获取内容
subscribe_url = f'https://ohayoo-pm.hf.space/api/v1/subscribe?token={token}&target=clash&list=0'
#print("正在获取订阅内容URL:", subscribe_url)

'''
print (urlencode(subscribe_url))

fullurl=baseurl+ urlencode(subscribe_url)
print (fullurl)
'''


# 获取订阅内容
subscribe_response = requests.get(subscribe_url)

# 检查请求是否成功
if subscribe_response.status_code == 200:
    # 第三步：将内容保存为clash.yaml文件
    with open('clash-auto-4h.yaml', 'w', encoding='utf-8') as file:
        file.write(subscribe_response.text)
    print("订阅内容已成功保存为clash-auto-4h.yaml文件")
else:
    print(f"获取订阅内容失败，HTTP状态码: {subscribe_response.status_code}")
    print("响应内容:", subscribe_response.text)
