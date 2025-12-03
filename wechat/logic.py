from chat import ChatManager

def run_chat_session(role_name="小羊"):
    """
    运行对话会话
    """
    chat_manager = ChatManager(role_name)
    
    try:
        while True:
            # 获取用户输入
            user_input = input("\n请输入你要说的话（输入\"再见\"退出）：")
            
            # 检查是否结束对话
            if chat_manager.check_end_conversation(user_input):
                print("对话结束")
                break
            
            # 添加用户消息
            chat_manager.add_user_message(user_input)
            
            # 获取AI回复
            try:
                assistant_reply = chat_manager.get_ai_response()
            except Exception as e:
                print(f"❌ 错误: {e}")
                continue
            
            # 添加AI回复
            chat_manager.add_assistant_message(assistant_reply)
            
            # 显示AI回复
            chat_manager.display_assistant_reply(assistant_reply)
            
            # 检查AI回复是否表示结束
            if chat_manager.check_assistant_end(assistant_reply):
                print("\n对话结束")
                break
                
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n\n发生错误: {e}")