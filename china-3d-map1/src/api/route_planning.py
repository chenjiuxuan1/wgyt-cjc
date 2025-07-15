import asyncio
import logging
import os
import sys
from flask import Blueprint, request, jsonify
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_deepseek import ChatDeepSeek

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # 输出到终端
        logging.FileHandler('route_planning.log')  # 同时保存到文件
    ]
)
logger = logging.getLogger(__name__)

class LogCollector:
    def __init__(self):
        self.logs = []

    def add_log(self, level, message):
        # 记录到列表
        self.logs.append(message)
        # 同时使用logger输出
        if level == 'error':
            logger.error(message)
        else:
            logger.info(message)

route_bp = Blueprint('route', __name__)

# 初始化 DeepSeek 大模型客户端
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key="sk-2c8484be8c2e4717ba3388c2c96a10a3"  # 请替换为您的API密钥
)

# 指定baidu_map.py的完整路径
baidu_map_path = r"F:\kshbs\vite-vue3-ts-demo\china-3d-map1 (1)\mcp_baidu\baidu_map.py"

async def process_route_query(question):
    log_collector = LogCollector()
    
    log_collector.add_log('info', f"开始处理问题: {question}")
    
    # 检查文件是否存在
    if not os.path.exists(baidu_map_path):
        error_msg = f"错误: baidu_map.py 文件不存在于路径: {baidu_map_path}"
        log_collector.add_log('error', error_msg)
        return error_msg, log_collector.logs

    # 创建服务器参数
    server_params = StdioServerParameters(
        command="python",
        args=[baidu_map_path],
    )
    log_collector.add_log('info', f"正在连接到百度地图MCP服务... 路径: {baidu_map_path}")

    try:
        # 使用 stdio_client 进行连接
        async with stdio_client(server_params) as (read, write):
            log_collector.add_log('info', "成功创建stdio客户端连接")
            
            async with ClientSession(read, write) as session:
                # 初始化连接
                await session.initialize()
                log_collector.add_log('info', "成功初始化MCP会话")

                # 加载工具
                tools = await load_mcp_tools(session)
                tool_names = [tool.name for tool in tools]
                log_collector.add_log('info', f"成功加载工具: {tool_names}")

                # 创建代理
                agent = create_react_agent(llm, tools)
                log_collector.add_log('info', "成功创建AI代理")

                # 调用代理处理问题
                log_collector.add_log('info', "开始调用AI代理处理问题...")
                try:
                    agent_response = await agent.ainvoke({"messages": question})
                    log_collector.add_log('info', "AI代理处理完成")
                    
                    # 提取回答
                    messages = agent_response.get("messages", [])
                    final_answer = None
                    
                    for message in messages:
                        if hasattr(message, "additional_kwargs") and "tool_calls" in message.additional_kwargs:
                            # 记录工具调用
                            tool_calls = message.additional_kwargs["tool_calls"]
                            for tool_call in tool_calls:
                                tool_name = tool_call["function"]["name"]
                                tool_args = tool_call["function"]["arguments"]
                                log_collector.add_log('info', f"工具调用: {tool_name}({tool_args})")
                        elif message.type == "tool":
                            log_collector.add_log('info', f"工具执行结果: {message.content}")
                        elif message.type == "ai":
                            final_answer = message.content
                            log_collector.add_log('info', f"AI回答: {final_answer}")
                    
                    return final_answer or "抱歉，无法处理您的请求", log_collector.logs
                except Exception as e:
                    error_msg = f"AI处理出错: {str(e)}"
                    log_collector.add_log('error', error_msg)
                    return error_msg, log_collector.logs
    except Exception as e:
        error_msg = f"连接服务器失败: {str(e)}"
        log_collector.add_log('error', error_msg)
        return error_msg, log_collector.logs

@route_bp.route('/api/route-planning', methods=['POST'])
def route_planning():
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        logger.warning("收到空请求")
        return jsonify({'error': '请提供问题', 'logs': []}), 400
    
    logger.info(f"收到新的路线规划请求: {question}")
    
    try:
        # 使用asyncio运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result, logs = loop.run_until_complete(process_route_query(question))
        loop.close()
        
        logger.info(f"请求处理完成，返回结果: {result}")
        return jsonify({
            'result': result,
            'logs': logs
        })
    except Exception as e:
        error_msg = f"服务器错误: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'error': error_msg,
            'logs': [f"服务器错误: {str(e)}"]
        }), 500 