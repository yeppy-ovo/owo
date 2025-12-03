from logic import run_chat_session

def main():
    """
    主程序入口
    """
    print("=== AI角色对话系统 ===")
    print("可选角色: 小羊, 小鸡")
    
    # 选择角色
    role_name = input("请选择角色 (默认小羊): ").strip()
    if not role_name or role_name not in ["小羊", "小鸡"]:
        role_name = "小羊"
        print(f"使用默认角色: {role_name}")
    
    # 运行对话
    run_chat_session(role_name)

if __name__ == "__main__":
    main()