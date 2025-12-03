from api import call_zhipu_api
import json

class ChatManager:
    def __init__(self, role_name):
        """
        初始化对话管理器
        """
        from roles import get_system_message
        
        # 获取系统消息
        system_message = get_system_message(role_name)
        
        # 初始化对话历史
        self.conversation_history = [{"role": "system", "content": system_message}]
        
        print("✓ 已加载初始记忆，开始对话（对话记录不会保存）")
    
    def add_user_message(self, user_input):
        """
        添加用户消息到对话历史
        """
        self.conversation_history.append({"role": "user", "content": user_input})
    
    def add_assistant_message(self, assistant_reply):
        """
        添加AI回复到对话历史
        """
        self.conversation_history.append({"role": "assistant", "content": assistant_reply})
    
    def get_ai_response(self):
        """
        获取AI回复
        """
        try:
            result = call_zhipu_api(self.conversation_history)
            assistant_reply = result['choices'][0]['message']['content']
            return assistant_reply
        except Exception as e:
            raise Exception(f"获取AI回复失败: {e}")
    
    def check_end_conversation(self, user_input):
        """
        检查是否结束对话
        """
        return user_input in ['再见']
    
    def check_assistant_end(self, assistant_reply):
        """
        检查AI回复是否表示结束
        """
        reply_cleaned = assistant_reply.strip().replace(" ", "").replace("！", "").replace("!", "").replace("，", "").replace(",", "")
        return reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned)
    
    def display_assistant_reply(self, assistant_reply):
        """
        显示AI回复
        """
        portrait = """
        (角色头像可以在这里定义)
        """
        print(portrait + "\n" + assistant_reply)
    
    def get_conversation_history(self):
        """
        获取当前对话历史
        """
        return self.conversation_history