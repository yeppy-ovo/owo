### **文件 `glm.py` 的知识点**

- **HTTP 请求与接口调用**：使用 `requests.post` 访问智谱 `chat/completions` 接口，提交 JSON 请求体并读取 JSON 响应。
- **请求头与鉴权**：通过 `Authorization` 传入密钥，`Content-Type` 设置为 `application/json`。
- **参数构造**：包含 `model`、`messages`（角色-内容格式）、`temperature` 等生成参数。
- **基础错误处理**：仅以 `status_code == 200` 作为成功条件，否则抛出异常并附带返回文本，便于排查。
- **响应解析**：从 `result['choices'][0]['message']['content']` 读取生成内容。
- **函数封装**：`call_zhipu_api(messages, model="glm-4.6")` 提供默认模型与统一调用入口。
- **用法示例**：演示如何构建 `messages` 并打印首条回复。

可改进点（安全与鲁棒性）：
- **密钥管理**：不要在代码中硬编码密钥，改用环境变量或配置文件。
- **网络健壮性**：增加超时、重试与更细粒度的异常捕获。
- **响应健壮性**：校验 `choices` 是否存在、长度是否>0，再取值。
- **可观测性**：为失败场景记录更明确的错误上下文（但避免泄露密钥）。

示例（改进版，使用环境变量与超时、校验）：

```python
import os
import requests

def call_zhipu_api(messages, model="glm-4.6", temperature=1.0, timeout=15):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        raise RuntimeError("缺少环境变量 ZHIPU_API_KEY")

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }
    data = {"model": model, "messages": messages, "temperature": temperature}

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=timeout)
        resp.raise_for_status()
        obj = resp.json()
    except requests.RequestException as e:
        raise RuntimeError(f"网络或HTTP错误: {e}") from e
    except ValueError:
        raise RuntimeError("响应非JSON格式")

    choices = obj.get("choices") or []
    if not choices or "message" not in choices[0] or "content" not in choices[0]["message"]:
        raise RuntimeError(f"响应结构异常: {obj}")
    return choices[0]["message"]["content"]
```

若需最小化改动，也可仅将密钥换为环境变量并加 `timeout`：

```python
headers = {
    "Authorization": os.getenv("ZHIPU_API_KEY"),
    "Content-Type": "application/json"
}
response = requests.post(url, headers=headers, json=data, timeout=15)
```

如需参考原始实现的关键片段：

```1:23:glm.py
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
```

### **文件 `101.py` 的知识点**

- **字符串相加**：`x`、`y` 是字符串，`print(x+y)` 会做字符串拼接，输出 `"12"` 而非数值加法。
- **类型转换**：进行数值加法需先转换为整数或浮点。

示例（数值加法与格式化输出）：

```python
x = "1"
y = "2"
print(int(x) + int(y))       # 3
print(f"{int(x) + int(y)}")  # 3，使用 f-string
```

也可从一开始使用数值类型：

```python
x = 1
y = 2
print(x + y)  # 3
```

- **基础语法**：变量赋值、`print` 输出、类型的重要性（`str` vs `int`）。


- 对 `glm.py` 的重点：HTTP/JSON 调用流程、鉴权、安全性与健壮性改进；响应内容定位路径。
- 对 `101.py` 的重点：字符串拼接与数值相加的差异、类型转换与格式化输出。
