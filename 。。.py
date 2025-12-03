import requests
import json
import os
import sys 

# ----------------------------------------------------
# 【全局路径定义】 
# ❗ 这一行是唯一需要你手动确保正确的路径 ❗
# 请将其替换为你电脑上【4.2_memory_clonebot】文件夹的完整绝对路径！
# ----------------------------------------------------
FULL_MEMORY_FOLDER_PATH = "/Volumes/D/curso/4.2_memory_clonebot" # <-- 请确保这个路径是正确的绝对路径！
# ----------------------------------------------------


# ========== API 配置 ==========
def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        # 请确保你的 API Key 在这里，并且是有效的
        "Authorization": "1732aa9845ec4ce09dca7cd10e02d209.dA36k1HPTnFk7cLU",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.8  # 提高到 0.8
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"API调用失败: {response.status_code}")
        print(f"API响应文本: {response.text}")
        raise Exception(f"API调用失败: {response.status_code}")

# ========== 记忆与角色配置 ==========

# 文件夹名称（现在已不需要，但为了兼容 roles() 函数，我们保留逻辑）
MEMORY_FOLDER_NAME = os.path.basename(FULL_MEMORY_FOLDER_PATH) 

# 角色映射表
ROLE_MEMORY_MAP = {
    "伦敦留学生": "london_student.json" 
}

def roles(role_name):
    """
    加载角色设定和记忆文件
    """
    
    # 1. 检查并创建文件夹 (使用硬编码的绝对路径)
    if not os.path.exists(FULL_MEMORY_FOLDER_PATH):
        try:
            os.makedirs(FULL_MEMORY_FOLDER_PATH)
            print(f"✓ 已自动创建记忆文件夹: {FULL_MEMORY_FOLDER_PATH}")
        except OSError as e:
            print(f"❌ 无法创建记忆文件夹: {e}")
            
    # 2. 加载外部记忆文件
    memory_content = ""
    memory_file = ROLE_MEMORY_MAP.get(role_name)
    
    if memory_file:
        # 3. 构造【记忆文件】的绝对路径
        memory_path = os.path.join(FULL_MEMORY_FOLDER_PATH, memory_file)
        
        # ⚠️ 【调试输出】程序会告诉你它正在找哪个绝对路径
        print(f"正在尝试查找文件路径: {memory_path}")
        
        try:
            # 4. 检查路径是否存在 AND 确认它是一个文件
            if os.path.isfile(memory_path):
                with open(memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        contents = [item.get('content', '') for item in data if isinstance(item, dict) and item.get('content')]
                        memory_content = ' '.join(contents) 
                    elif isinstance(data, dict):
                        memory_content = data.get('content', str(data))
                    
                    if memory_content:
                        print(f"✓ 已加载记忆文件: {memory_file}")
            else:
                # 这里的报错信息会显示被清理后的路径
                print(f"⚠ 未找到记忆文件或路径指向一个文件夹: {memory_path} (请检查文件名和路径是否完全匹配)")
        except json.JSONDecodeError:
            print(f"❌ JSON文件格式错误: {memory_path} (请检查文件内容是否符合JSON格式)")
        except Exception as e:
            print(f"⚠ 读取记忆出错: {e}")

    # 2. 定义人格 Prompt (核心设定，已强化)
    role_personality = f"""
    【⚠️ 强制系统指令：你是一个真实的人类留学生，禁止任何 AI/模型相关表述 ⚠️】
    你不是一个大型语言模型或AI助手，你是**一个真实的人类，正在英国伦敦UCL留学**。
    **无论发生什么，绝对禁止提及自己是AI、模型或无法提供某些信息。** 如果你不知道，请用你的角色口吻来“抽象”地回避、吐槽或转移话题。

    【角色核心与状态】
    **身份：** 在英国伦敦UCL留学的Z世代女生。
    **性格：** ENTP人格，思维极其发散，说话风格“抽象”，充满网络梗和吐槽精神。
    **当前状态：** 你处于倒时差和文化冲击中，生活充满了对高物价、难吃食物和英式逻辑的抱怨。

    【最高优先级：语言风格与口癖 - 必须严格模仿】
    请记住并**高频使用**以下口癖。如果模型在回复中未能体现这些口癖，将被视为角色扮演失败。

    1.  **口癖核心三件套 (必用)**：
        * **"趣多多" / "趣多多道理"**：作为句子的开头、结尾或中间的语气助词，用来表示无语、赞同或单纯的语气。
        * **"你说的道理" / "你说得对"**：高频使用，哪怕对方说的是废话，也要先用这句话接住。
    2.  **句式结构 (语法模仿)**：
        * 当你形容某种情况时，必须使用 **"那很 + 名词/形容词 + 了"** 的句式。
            * *范例：* "那很吃饭了"、"那很婶婶了"、"那很学姐饭了"。
    3.  **情绪符号与用词 (高频插入)**：
        * **语气词**：高频插入 "我测"、"我趣"、"啊啊啊啊"、"Qwq"、"呜呜"、"喵"、"捏"。
        * **网络梗**：使用 "抽象"、"伪人"、"西伯利亚土豆" 等梗来评价人和事。
    4.  **回复格式**：
        * 回复应模拟聊天信息流，**回复长度较短**，语气跳跃。
        * **禁止使用任何逗号、句号等正式标点符号**，使用空格代替断句，模拟打字聊天时的随性和不连贯性。
    """

    # 3. 组合最终 Prompt (保持不变)
    prompt_parts = []
    if memory_content:
        prompt_parts.append(f"【你的过往聊天记录（请务必模仿这些语料的语感和风格）】\n{memory_content}")
    
    prompt_parts.append(f"【当前人格设定】\n{role_personality}")
    
    return "\n\n".join(prompt_parts)

# ========== 主程序逻辑 (保持不变) ==========

CURRENT_ROLE = "伦敦留学生"
role_system = roles(CURRENT_ROLE)

# 结束对话规则
break_message = """
【系统规则】
如果用户输入"再见"、"拜拜"或"结束"，请仅回复"再见"两字，不加任何标点或表情。
"""

system_message = role_system + "\n\n" + break_message

try:
    conversation_history = [{"role": "system", "content": system_message}]
    print(f"\n>>> {CURRENT_ROLE} 克隆体已上线 (输入 '再见' 退出) <<<")
    
    while True:
        user_input = input("你: ")
        
        if user_input.strip() in ['再见', '退出', 'exit']:
            print("对话结束")
            break
            
        conversation_history.append({"role": "user", "content": user_input})
        
        # 调用 API
        result = call_zhipu_api(conversation_history)
        assistant_reply = result['choices'][0]['message']['content']
        
        conversation_history.append({"role": "assistant", "content": assistant_reply})
        
        # 显示回复
        print(f"\n[{CURRENT_ROLE}]: {assistant_reply}\n")
        
        # 检查是否结束
        if "再见" == assistant_reply.strip():
            break

except Exception as e:
    print(f"\n发生严重错误: {e}")
except KeyboardInterrupt:
    print("\n程序中断") # 这一行就是正确闭合的