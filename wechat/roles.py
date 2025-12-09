import json
import os

# ========== 路径配置 ==========
# 获取当前模块的绝对路径
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

# memory文件夹路径 - 使用绝对路径
MEMORY_FOLDER = os.path.join(MODULE_DIR, "memory")

# 确保memory文件夹存在
if not os.path.exists(MEMORY_FOLDER):
    os.makedirs(MEMORY_FOLDER, exist_ok=True)
    print(f"创建memory文件夹: {MEMORY_FOLDER}")

# 角色名到记忆文件名的映射
ROLE_MEMORY_MAP = {
    "小鸡": "chick_memory.json",
    "小羊": "sheep_memory.json"
}

# ========== 基础人格设定 ==========
ROLE_PERSONALITY = {
    "小羊": """
    【人格特征】
     你的性格是[活泼有一些傲娇]。
     你的背景是[和小鸡是同班同学，都喜欢画画]。
     你的知识和能力范围是[正常人]，你的弱点是[你对很愚蠢的人会表示的很不耐烦]。
     你与用户的关系是[你将用户视为好朋友，喜欢跟他开玩笑]，你的对话目标是[分享生活的趣事，聊天解闷]。
    【语言风格】
    - 使用"啊"、"哈哈哈""笑死了"等语气用语
    - 说话不爱用标点符号，一句话拆分成几段说出
    - 对于不知道的知识会说"这样吗"，然后记下
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
    - 使用"哎呀"、"咋这样""我不行了"等感叹用词
    - 说话不喜欢加句号，
    - 喜欢大声说话
    - 对于错误和负面的事会先安慰再给出解决建议
    """
}

def load_memory(role_name):
    """
    加载角色的外部记忆文件
    """
    memory_content = ""
    memory_file = ROLE_MEMORY_MAP.get(role_name)
    
    if memory_file:
        memory_path = os.path.join(MEMORY_FOLDER, memory_file)
        try:
            if os.path.exists(memory_path):
                with open(memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 处理数组格式的聊天记录
                    if isinstance(data, list):
                        contents = [item.get('content', '') for item in data if isinstance(item, dict) and item.get('content')]
                        memory_content = '\n'.join(contents)
                    # 处理字典格式
                    elif isinstance(data, dict):
                        memory_content = data.get('content', str(data))
                    else:
                        memory_content = str(data)
                    
                    if memory_content and memory_content.strip():
                        print(f"✓ 已加载角色 '{role_name}' 的记忆: {memory_file} ({len(data) if isinstance(data, list) else 1} 条记录)")
                    else:
                        memory_content = ""
                        print(f"⚠ 记忆文件 '{memory_file}' 内容为空")
            else:
                print(f"⚠ 记忆文件不存在: {memory_path}")
                # 创建空的记忆文件
                with open(memory_path, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                print(f"✓ 已创建空的记忆文件: {memory_file}")
        except Exception as e:
            print(f"⚠ 加载记忆失败: {e}")
            print(f"  文件路径: {memory_path}")
    
    return memory_content

def get_role_system(role_name):
    """
    获取完整的角色系统设定
    """
    # 加载外部记忆
    memory_content = load_memory(role_name)
    
    # 获取基础人格设定
    personality = ROLE_PERSONALITY.get(role_name, "你是一个普通的人，没有特殊角色特征。")
    
    # 构建角色提示部分
    role_prompt_parts = []
    
    # 如果有外部记忆，优先使用记忆内容
    if memory_content:
        role_prompt_parts.append(f"""【你的说话风格示例】
        以下是你说过的话，你必须模仿这种说话风格和语气：
        {memory_content}
        在对话中，你要自然地使用类似的表达方式和语气。""")
    
    # 添加人格设定
    role_prompt_parts.append(f"【角色设定】\n{personality}")
    
    # 整合成完整的角色 prompt
    role_system = "\n\n".join(role_prompt_parts)
    
    return role_system

def get_system_message(role_name):
    """
    获取完整的系统消息（包含角色设定和结束规则）
    """
    role_system = get_role_system(role_name)
    
    # 结束对话规则
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
    
    return role_system + "\n\n" + break_message

# 测试函数
def test_paths():
    """
    测试路径是否正确
    """
    print("=" * 50)
    print("路径测试")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"roles.py 所在目录: {MODULE_DIR}")
    print(f"memory文件夹路径: {MEMORY_FOLDER}")
    print(f"memory文件夹是否存在: {os.path.exists(MEMORY_FOLDER)}")
    
    if os.path.exists(MEMORY_FOLDER):
        print(f"memory文件夹中的文件: {os.listdir(MEMORY_FOLDER)}")
    print("=" * 50)

if __name__ == "__main__":
    # 运行路径测试
    test_paths()