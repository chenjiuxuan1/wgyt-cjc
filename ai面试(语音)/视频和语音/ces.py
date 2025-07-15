import ollama

def chat_with_ollama():
    # 创建客户端连接
    client = ollama.Client()
    # 存储对话历史
    messages = []
    
    print("开始与AI对话（输入 'quit' 或 'exit' 结束对话）")
    
    while True:
        # 获取用户输入
        user_input = input("\n你: ")
        
        # 检查是否退出
        if user_input.lower() in ['quit', 'exit']:
            print("对话结束！")
            break
        
        # 添加用户消息到历史
        messages.append({
            'role': 'user',
            'content': user_input
        })
        
        try:
            # 获取AI响应
            response = client.chat(model='llama3.2', messages=messages)
            ai_response = response['message']['content']
            
            # 添加AI响应到历史
            messages.append({
                'role': 'assistant',
                'content': ai_response
            })
            
            # 打印AI响应
            print("\nAI:", ai_response)
            
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
            continue

if __name__ == "__main__":
    chat_with_ollama()