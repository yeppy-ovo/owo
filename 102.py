import requests
import json

from requests.utils import stream_decode_response_unicode

def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "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",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.5   
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")

role_system = ["你是一只小猫，在问道小猫不会的知识的时候喵喵叫", "你是小猫的主人，你知道小猫不会的知识","你是一个普通人，不认识小猫和他的主人"]
import random
current_role = random.choice(role_system)
break_message = "你要尽力伪装你的身份，当我猜到你的身份的时候，承认"
# 多轮对话循环，直到用户输入 '再见' 结束
while True:  # 表示“当条件为真时一直循环”。由于 True 永远为真，这个循环会一直运行，直到遇到 break 才会停止。
    user_input = input("请输入你要说的话：")
    messages = [
        {"role": "user", "content": break_message + current_role + user_input}
    ]
    result = call_zhipu_api(messages)
    assistant_reply = result['choices'][0]['message']['content']
    print(assistant_reply)
    if "我承认" in assistant_reply or "你说得对" in assistant_reply or "被你发现了" in assistant_reply:
        print("恭喜你！你成功猜出了角色的身份或秘密！")
        break
