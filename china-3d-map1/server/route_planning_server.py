from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_deepseek import ChatDeepSeek

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 初始化 DeepSeek 大模型客户端
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key="sk-2c8484be8c2e4717ba3388c2c96a10a3"  # 请替换为您的API密钥
)

# 指定baidu_map.py的完整路径
baidu_map_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mcp_baidu", "baidu_map.py")

async def process_route_query(question):
    """处理路线查询"""
    logger.info(f"开始处理问题: {question}")
    
    # 创建服务器参数，使用绝对路径
    server_params = StdioServerParameters(
        command="python",
        args=[baidu_map_path],
    )
    logger.info(f"正在连接到百度地图MCP服务... 路径: {baidu_map_path}")

    try:
        # 使用 stdio_client 进行连接
        async with stdio_client(server_params) as (read, write):
            logger.info("成功创建stdio客户端连接")
            
            async with ClientSession(read, write) as session:
                try:
                    # 初始化连接
                    await session.initialize()
                    logger.info("成功初始化MCP会话")

                    # 加载工具
                    tools = await load_mcp_tools(session)
                    logger.info(f"成功加载工具: {[tool.name for tool in tools]}")

                    # 创建代理
                    agent = create_react_agent(llm, tools)
                    logger.info("成功创建AI代理")

                    # 构建系统提示信息
                    system_prompt = """你是一个专业的路线规划助手。当用户提供起点和终点时，你需要：
1. 使用map_geocode工具将地址转换为坐标
2. 使用map_directions工具规划路线
3. 分析并总结路线信息，包括距离、时间和具体路线步骤
4. 如果找不到路线，给出合适的建议

请用中文回答，保持专业和友好的语气。

注意：请确保在使用工具之前先获取坐标，然后再进行路线规划。每次调用工具后要检查结果是否成功。"""

                    # 调用代理处理问题
                    logger.info("开始调用AI代理处理问题...")
                    
                    # 初始化变量
                    agent_response = None
                    messages = []
                    final_answer = None
                    
                    try:
                        agent_response = await agent.ainvoke({
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": question}
                            ]
                        })
                        logger.info("AI代理处理完成")
                        
                        # 提取回答
                        if agent_response:
                            messages = agent_response.get("messages", [])
                            
                            for message in messages:
                                if hasattr(message, "additional_kwargs") and "tool_calls" in message.additional_kwargs:
                                    # 记录工具调用
                                    tool_calls = message.additional_kwargs["tool_calls"]
                                    for tool_call in tool_calls:
                                        tool_name = tool_call["function"]["name"]
                                        tool_args = tool_call["function"]["arguments"]
                                        logger.info(f"工具调用: {tool_name}({tool_args})")
                                elif message.type == "tool":
                                    # 记录工具执行结果
                                    logger.info(f"工具执行结果: {message.content}")
                                elif message.type == "ai" and message.content:
                                    final_answer = message.content
                                    logger.info(f"AI回答: {final_answer}")
                        
                        if not final_answer or final_answer == "Hello! How can I assist you today?":
                            final_answer = "抱歉，我暂时无法处理这个路线规划请求，请确保提供了明确的起点和终点。"
                        
                    except Exception as e:
                        logger.error(f"AI代理调用失败: {str(e)}")
                        logger.error(f"错误类型: {type(e).__name__}")
                        logger.error(f"详细错误信息: {e.__dict__}")
                        final_answer = f"路线规划失败: {str(e)}"
                    
                    return final_answer

                except Exception as e:
                    error_msg = f"MCP会话处理出错: {str(e)}"
                    logger.error(error_msg)
                    return error_msg
    except Exception as e:
        error_msg = f"处理请求时出现错误: {str(e)}"
        logger.error(error_msg)
        return error_msg

@app.route('/api/route-planning', methods=['POST'])
def route_planning():
    data = request.get_json()
    question = data.get('question')
    
    if not question or question == "test":
        logger.warning("收到空请求或测试请求")
        return jsonify({'error': '请提供具体的起点和终点'}), 400
    
    logger.info(f"收到新的路线规划请求: {question}")
    
    try:
        # 使用asyncio运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(process_route_query(question))
        loop.close()
        
        # 如果返回的是默认回答，则返回错误提示
        if result in ["你好！请问有什么可以帮您的吗？", "Hello! How can I assist you today?"]:
            return jsonify({'error': '请提供具体的起点和终点位置'}), 400
            
        logger.info(f"请求处理完成，返回结果: {result}")
        return jsonify({'result': result})
    except Exception as e:
        error_msg = f"服务器错误: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    logger.info("路线规划服务器启动...")
    logger.info(f"baidu_map.py 路径: {baidu_map_path}")
    # 检查文件是否存在
    if not os.path.exists(baidu_map_path):
        logger.error(f"错误: baidu_map.py 文件不存在于路径: {baidu_map_path}")
        exit(1)
    app.run(host='0.0.0.0', port=5123)  # 修改host为0.0.0.0以支持外部访问 