import streamlit as st
import requests
import json
import os 
import traceback # 用于更详细的错误追踪

# ==========================================================
# ⚡ 智谱 AI API 调用函数
# ==========================================================

# ⚠️ 强烈建议：如果您部署到 Streamlit Cloud，请在 Secrets 中设置 API_KEY。
# 否则，请将您的 API Key 替换到下面的 api_key 变量中。

def call_zhipu_api(messages, model="glm-4-flash"):
    """调用智谱 AI API 获取回复。"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    # --- API Key 获取 ---
    # 优先从 Streamlit Secrets 中读取，如果没有，使用硬编码（不推荐）
    try:
        api_key = st.secrets["API_KEY"]
    except:
        # 如果您没有设置 Secrets，请将 API Key 替换到这里
        api_key = "1732aa9845ec4ce09dca7cd10e02d209.dA36k1HPTnFk7cLU" 
        if api_key == "YOUR_API_KEY_HERE":
             st.error("API Key 未设置。请在 Streamlit Secrets 或代码中配置正确的 API Key。")
             return None
    # ----------------------

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.7  
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status() # 如果状态码不是 200，则抛出 HTTPError
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API调用失败或网络错误: {e}")
        return None
    except Exception as e:
        st.error(f"发生未知错误: {e}")
        return None

# ==========================================================
# 💾 初始记忆系统 (Streamlit 缓存加载)
# ==========================================================

# 角色名到记忆文件名的映射
ROLE_MEMORY_MAP = {
    "小鸡": "chick_memory.json",
    "小羊": "sheep_memory.json"
}

@st.cache_data(show_spinner="正在加载角色记忆文件...")
def load_memory_data(role_name):
    """
    为 Streamlit Cloud 部署设计的加载函数，只在应用的根目录寻找文件。
    请确保 chick_memory.json 和 sheep_memory.json 已提交到 GitHub 根目录。
    """
    memory_file = ROLE_MEMORY_MAP.get(role_name)
    if not memory_file:
        return "" 

    file_path = memory_file
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            memory_content = ""
            if isinstance(data, list):
                # 处理数组格式：提取所有 content 字段
                contents = [item.get('content', '') for item in data if isinstance(item, dict) and item.get('content')]
                memory_content = '\n'.join(contents)
            elif isinstance(data, dict):
                # 处理字典格式：获取 'content' 字段
                memory_content = data.get('content', str(data))
            else:
                memory_content = str(data)

            if not memory_content or not memory_content.strip():
                 st.warning(f"⚠ 记忆文件 '{file_path}' 已加载但内容为空。")
                 return ""
                 
            st.toast(f"✅ 成功加载 {role_name} 的记忆。")
            return memory_content
            
    except FileNotFoundError:
        st.error(f"❌ 严重错误：记忆文件 '{file_path}' 未找到！
