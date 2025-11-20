import requests
import json

def call_zhipu_api(messages, model="glm-4.6"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "bb9aed369c3445dd8dca96e5f71d3a99.BaOWdkr1dNBxhboL",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 1.0
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")

role_system = "你是一个幽默风趣的编程导师，擅长用简单易懂的方式解释复杂概念。"
messages = [
    {"role": "user", "content": role_system+"你好，请介绍一下自己"}
]


# 使用示例

result = call_zhipu_api(messages)
print(result['choices'][0]['message']['content'])