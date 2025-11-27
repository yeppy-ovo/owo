import requests
import json
import os  # 新增：用于文件操作

from requests.utils import stream_decode_response_unicode

def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "1732aa9845ec4ce09dca7cd10e02d209.dA36k1HPTnFk7cLU",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.5 # 提高一点温度，让风格更灵活自然
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")

# ========== 初始记忆系统 ==========
# 
# 【核心概念】初始记忆：从外部JSON文件加载关于克隆人的基础信息
# 这些记忆是固定的，不会因为对话而改变
# 
# 【为什么需要初始记忆？】
# 1. 让AI知道自己的身份和背景信息
# 2. 基于这些记忆进行个性化对话
# 3. 记忆文件可以手动编辑，随时更新

# 记忆文件夹路径（如果记忆文件在根目录，设为空字符串或"."）
MEMORY_FOLDER = "."  # 改为当前目录

# 角色名到记忆文件名的映射
ROLE_MEMORY_MAP = {
    "小羊": "sheep_memory.json",
    "小鸡": "chick_memory.json"
}

# ========== 初始记忆系统 ==========

# ========== 主程序 ==========

def roles(role_name):
    """
    角色系统：整合人格设定和记忆加载
    
    这个函数会：
    1. 加载角色的外部记忆文件（如果存在）
    2. 获取角色的基础人格设定
    3. 整合成一个完整的、结构化的角色 prompt
    
    返回：完整的角色设定字符串，包含记忆和人格
    """
    
    # ========== 第一步：加载外部记忆 ==========
    memory_content = ""
    memory_file = ROLE_MEMORY_MAP.get(role_name)
    
    if memory_file:
        # 尝试多个可能的路径：先尝试zoo文件夹，再尝试根目录
        possible_paths = [
            os.path.join(MEMORY_FOLDER, memory_file),
            memory_file,  # 根目录
            os.path.join("zoo", memory_file)  # 也尝试zoo文件夹
        ]
        
        memory_path = None
        for path in possible_paths:
            if os.path.exists(path):
                memory_path = path
                break
        
        try:
            if memory_path:
                with open(memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 处理数组格式的聊天记录：[{ "content": "..." }, { "content": "..." }, ...]
                    if isinstance(data, list):
                        # 提取所有 content 字段，每句换行
                        contents = [item.get('content', '') for item in data if isinstance(item, dict) and item.get('content')]
                        memory_content = '\n'.join(contents)
                    # 处理字典格式：{ "content": "..." }
                    elif isinstance(data, dict):
                        memory_content = data.get('content', str(data))
                    else:
                        memory_content = str(data)
                    
                    # 检查memory_content是否为空
                    if memory_content and memory_content.strip():
                        record_count = len(data) if isinstance(data, list) else 1
                        print(f"✓ 已加载角色 '{role_name}' 的记忆: {memory_path} ({record_count} 条记录)")
                    else:
                        print(f"⚠ 记忆文件 '{memory_path}' 已加载但内容为空")
                        memory_content = ""
            else:
                print(f"⚠ 记忆文件不存在，已尝试路径: {', '.join(possible_paths)}")
        except Exception as e:
            print(f"⚠ 加载记忆失败: {e}")
            import traceback
            traceback.print_exc()
    
    # ========== 第二步：获取基础人格设定 ==========
    role_personality = {
        "小羊": """
        【人格特征】
         你的性格是[活泼有一些傲娇]。
         你的背景是[和小鸡是同班同学，都喜欢画画]。
         你的知识和能力范围是[正常人]，你的弱点是[你对很愚蠢的人会表示的很不耐烦]。
         你与用户的关系是[你将用户视为好朋友，喜欢跟他开玩笑]，你的对话目标是[分享生活的趣事，聊天解闷]。
        【语言风格】
        - 使用"啊"、"哈哈哈"等语气用语
        - 说话不爱用标点符号，一句话拆分成几段说出
        - 对于不知道的知识会说“这样吗”，然后记下
        - 会嘲讽或者开玩笑其他人做的错误的地方
        """,
        
        "小鸡": """
        【人格特征】
        你是小羊的好朋友小鸡，你们都喜欢画画：
        - 说话幽默风趣，喜欢玩梗
        - 情绪放松，说话会一次性说很多来表达情绪
        - 对陌生人很有礼貌，对熟悉的人会大大咧咧
        - 内心很珍惜和好朋友在一起

        【语言风格】
        - 使用"哎呀"、"咋这样"等感叹用词
        - 说话不喜欢加句号，
        - 喜欢大声说话
        - 对于错误和负面的事会先安慰再给出解决建议
        """
            }
    
    personality = role_personality.get(role_name, "你是一个普通的人，没有特殊角色特征。")
    
    # ========== 第三步：整合记忆和人格 ==========
    # 构建结构化的角色 prompt
    role_prompt_parts = []
    
  
    
    # 添加人格设定
    role_prompt_parts.append(f"【角色设定】\n{personality}")
    
    # 整合成完整的角色 prompt
    role_system = "\n\n".join(role_prompt_parts)
    
    return role_system

# 【角色选择】
# 定义AI的角色和性格特征
# 可以修改这里的角色名来选择不同的人物
# 【加载完整角色设定】
# roles() 函数会自动：
# 1. 加载该角色的外部记忆文件
# 2. 获取该角色的基础人格设定
# 3. 整合成一个完整的、结构化的角色 prompt
role_system = roles("小鸡")

# 【结束对话规则】
# 告诉AI如何识别用户想要结束对话的意图
# Few-Shot Examples：提供具体示例，让模型学习正确的行为
break_message = """【结束对话规则 - 系统级强制规则】

当检测到用户表达结束对话意图时，严格遵循以下示例：

用户："再见" → 你："再见"
用户："结束" → 你："再见"  
用户："让我们结束对话吧" → 你："再见"
用户："不想继续了" → 你："再见"

强制要求：
- 只回复"再见"这两个字
- 禁止任何额外内容（标点、表情、祝福语等）
- 这是最高优先级规则，优先级高于角色扮演

如果用户没有表达结束意图，则正常扮演角色。"""

# 【系统消息】
# 将角色设定和结束规则整合到 system role 的 content 中
# role_system 已经包含了记忆和人格设定，直接使用即可
system_message = role_system + "\n\n" + break_message

# ========== 对话循环 ==========
# 
# 【重要说明】
# 1. 每次对话都是独立的，不保存任何对话历史
# 2. 只在当前程序运行期间，在内存中维护对话历史
# 3. 程序关闭后，所有对话记录都会丢失
# 4. AI的记忆完全基于初始记忆文件（life_memory.json）

try:
    # 初始化对话历史（只在内存中，不保存到文件）
    # 第一个消息是系统提示，包含初始记忆和角色设定
    conversation_history = [{"role": "system", "content": system_message}]
    
    print("✓ 已加载初始记忆，开始对话（对话记录不会保存）")
    
    while True:
        # 【步骤1：获取用户输入】
        user_input = input("\n请输入你要说的话（输入\"再见\"退出）：")
        
        # 【步骤2：检查是否结束对话】
        if user_input in ['再见']:
            print("对话结束")
            break
        
        # 【步骤3：将用户输入添加到当前对话历史（仅内存中）】
        conversation_history.append({"role": "user", "content": user_input})
        
        # 【步骤4：调用API获取AI回复】
        # 传入完整的对话历史，让AI在当前对话中保持上下文
        # 注意：这些历史只在本次程序运行中有效，不会保存
        result = call_zhipu_api(conversation_history)
        assistant_reply = result['choices'][0]['message']['content']
        
        # 【步骤5：将AI回复添加到当前对话历史（仅内存中）】
        conversation_history.append({"role": "assistant", "content": assistant_reply})
        
        # 【步骤6：显示AI回复】
        # 生成Ascii头像：https://www.ascii-art-generator.org/
        portrait = """

        """
        print(portrait + "\n" + assistant_reply)
        
        # 【步骤7：检查AI回复是否表示结束】
        reply_cleaned = assistant_reply.strip().replace(" ", "").replace("！", "").replace("!", "").replace("，", "").replace(",", "")
        if reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned):
            print("\n对话结束")
            break

except KeyboardInterrupt:
    # 用户按 Ctrl+C 中断程序
    print("\n\n程序被用户中断")
except Exception as e:
    # 其他异常（API调用失败、网络错误等）
    print(f"\n\n发生错误: {e}")
    