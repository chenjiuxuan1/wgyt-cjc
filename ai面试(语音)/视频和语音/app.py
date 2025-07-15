from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import os
import ollama
import uuid
import sqlite3
import json
import random
import base64
import time
import traceback  # 添加traceback模块用于详细错误记录
import pickle  # 用于序列化会话数据
import threading  # 用于线程锁
import re  # 用于正则表达式

# 导入面部表情分析器（添加更多错误处理）
FACE_EMOTION_AVAILABLE = False
try:
    # 先尝试直接导入
    from face_emotion_analyzer import FaceEmotionAnalyzer
    FACE_EMOTION_AVAILABLE = True
    print("成功导入面部表情分析模块")
except ImportError as e:
    # 如果直接导入失败，尝试相对导入
    try:
        # 检查文件是否存在
        face_analyzer_path = os.path.join(os.path.dirname(__file__), 'face_emotion_analyzer.py')
        if os.path.exists(face_analyzer_path):
            print(f"面部表情分析模块文件存在于: {face_analyzer_path}")
            # 尝试使用exec导入
            import importlib.util
            spec = importlib.util.spec_from_file_location("face_emotion_analyzer", face_analyzer_path)
            face_emotion_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(face_emotion_module)
            FaceEmotionAnalyzer = face_emotion_module.FaceEmotionAnalyzer
            FACE_EMOTION_AVAILABLE = True
            print("通过路径导入面部表情分析模块成功")
        else:
            print(f"面部表情分析模块文件不存在: {face_analyzer_path}")
            
            # 尝试使用模拟版本
            mock_path = os.path.join(os.path.dirname(__file__), 'mock_face_emotion_analyzer.py')
            if os.path.exists(mock_path):
                print(f"找到模拟面部表情分析模块: {mock_path}")
                spec = importlib.util.spec_from_file_location("mock_face_emotion_analyzer", mock_path)
                mock_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mock_module)
                FaceEmotionAnalyzer = mock_module.FaceEmotionAnalyzer
                FACE_EMOTION_AVAILABLE = True
                print("使用模拟面部表情分析模块替代")
            else:
                print("未找到模拟面部表情分析模块")
    except Exception as inner_e:
        print(f"警告: 面部表情分析模块导入失败: {str(inner_e)}")
        print("面部表情识别功能将不可用")
        print("如需启用此功能，请运行 python install_dependencies.py 安装所需依赖")
        print("或者使用以下命令复制模拟面部表情分析器:")
        print("python -c \"import shutil; shutil.copy('视频和语音/mock_face_emotion_analyzer.py', '视频和语音/face_emotion_analyzer.py')\"")

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 配置密钥
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['XFYUN_APPID'] = os.getenv('XFYUN_APPID', '9d7eafb5')
app.config['XFYUN_API_KEY'] = os.getenv('XFYUN_API_KEY', '07d0a7de3ccb3116c22b8de9c374b1b2')
# 增加请求体大小限制，设置为100MB (默认是16MB)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# 创建保存文件的目录
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"创建上传目录: {os.path.abspath(UPLOAD_FOLDER)}")
else:
    print(f"上传目录已存在: {os.path.abspath(UPLOAD_FOLDER)}")

# 创建会话存储目录
SESSIONS_FOLDER = os.path.join(UPLOAD_FOLDER, 'sessions')
if not os.path.exists(SESSIONS_FOLDER):
    os.makedirs(SESSIONS_FOLDER)
    print(f"创建会话存储目录: {os.path.abspath(SESSIONS_FOLDER)}")
else:
    print(f"会话存储目录已存在: {os.path.abspath(SESSIONS_FOLDER)}")

# 存储面试数据的字典（内存缓存，会定期同步到文件）
interview_sessions = {}
# 添加线程锁，防止并发写入导致的文件损坏
session_lock = threading.Lock()

# 从文件加载会话数据
def load_session_from_file(session_id):
    try:
        session_file = os.path.join(SESSIONS_FOLDER, f"{session_id}.pickle")
        if os.path.exists(session_file):
            with open(session_file, 'rb') as f:
                return pickle.load(f)
        return None
    except Exception as e:
        print(f"从文件加载会话数据失败: {str(e)}")
        return None

# 保存会话数据到文件
def save_session_to_file(session_id, session_data):
    try:
        with session_lock:
            session_file = os.path.join(SESSIONS_FOLDER, f"{session_id}.pickle")
            with open(session_file, 'wb') as f:
                pickle.dump(session_data, f)
            print(f"会话数据已保存至: {session_file}")
        return True
    except Exception as e:
        print(f"保存会话数据失败: {str(e)}")
        traceback.print_exc()
        return False

# 获取会话数据，优先从内存获取，内存中不存在则从文件加载
def get_session_data(session_id):
    if session_id in interview_sessions:
        return interview_sessions[session_id]
    
    # 尝试从文件加载
    session_data = load_session_from_file(session_id)
    if session_data:
        # 加载到内存缓存
        interview_sessions[session_id] = session_data
        return session_data
    
    return None

# 数据库配置
DATABASE = 'ms.db'

# 数据库连接函数
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# 初始化数据库
def init_db():
    conn = get_db_connection()
    
    # 创建面试题表
    conn.execute('''
    CREATE TABLE IF NOT EXISTS mstk (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wt TEXT NOT NULL,          -- 问题
        dn TEXT NOT NULL,          -- 答案
        gw TEXT NOT NULL,          -- 岗位
        difficulty TEXT DEFAULT '中等'  -- 难度级别
    )
    ''')
    
    # 检查是否已有数据
    cursor = conn.execute('SELECT COUNT(*) FROM mstk')
    count = cursor.fetchone()[0]
    
    # 如果没有数据，插入初始面试题
    if count == 0:
        insert_initial_questions(conn)
    
    conn.commit()
    conn.close()

# 插入初始面试题
def insert_initial_questions(conn):
    positions = [
        '数据开发', '数据分析', '算法工程师', 
        '前端工程师', '软件工程师', '大模型工程师'
    ]
    
    questions_by_position = {
        '数据开发': [
            {
                'wt': '什么是ETL过程？它在数据工程中有何作用？',
                'dn': 'ETL是提取、转换和加载数据的过程。它确保数据质量、一致性和可用性，支持业务分析和决策。',
                'difficulty': '简单'
            },
            {
                'wt': '请列举几种优化Spark作业性能的方法',
                'dn': '优化Spark性能：合理分区、缓存频繁使用的数据、广播小表、使用DataFrame替代RDD、调整并行度、优化序列化方式、内存调优。',
                'difficulty': '中等'
            },
            {
                'wt': '如何设计数据仓库架构处理实时和批量数据？',
                'dn': '现代数据仓库应包含：数据源层、接入层(Kafka)、存储层、处理层(批处理和流处理)、服务层。实时数据通过Kafka进Flink处理，批量数据通过ETL处理。数据质量通过验证规则和监控确保。',
                'difficulty': '困难'
            }
        ],
        '数据分析': [
            {
                'wt': '什么是相关性分析？如何判断变量间相关强度？',
                'dn': '相关性分析研究变量间关系，主要通过相关系数判断强度。|r|<0.3为弱相关，0.3≤|r|<0.7为中等相关，|r|≥0.7为强相关。',
                'difficulty': '简单'
            },
            {
                'wt': 'A/B测试如何确定样本量及评估统计显著性？',
                'dn': '确定样本量需考虑：最小可检测效应量、统计功效、显著性水平、基线转化率。评估显著性使用假设检验计算p值，通常p<0.05时认为有统计显著性。',
                'difficulty': '中等'
            },
            {
                'wt': '电商平台用户增长停滞，如何通过数据分析找原因并提出改进？',
                'dn': '分析思路：用户漏斗分析、同期群分析、用户分层分析、获客渠道分析、竞品分析、用户反馈分析。改进策略：针对性营销、产品体验优化、精准用户画像、推荐算法优化。',
                'difficulty': '困难'
            }
        ],
        '算法工程师': [
            {
                'wt': '请解释梯度下降算法的基本原理及主要变种',
                'dn': '梯度下降通过计算损失函数梯度更新模型参数。主要变种：批量梯度下降(BGD)、随机梯度下降(SGD)、小批量梯度下降、动量梯度下降、AdaGrad、RMSProp、Adam。',
                'difficulty': '简单'
            },
            {
                'wt': 'BERT模型的预训练过程和微调方法是什么？',
                'dn': 'BERT预训练：使用掩码语言模型(MLM)和下一句预测(NSP)两个任务，在大规模文本上训练。微调：在特定任务上使用预训练模型，添加任务相关输出层，使用较小学习率微调。',
                'difficulty': '中等'
            },
            {
                'wt': '如何设计推荐系统处理冷启动、实时更新和大规模数据？',
                'dn': '推荐系统设计：数据层(用户画像、物品特征)、算法层(协同过滤、内容推荐)、策略层、服务层。冷启动通过内容推荐和兴趣问卷解决。实时更新用在线学习框架。大规模数据用分布式存储和处理。',
                'difficulty': '困难'
            }
        ],
        '前端工程师': [
            {
                'wt': '解释CSS盒模型和box-sizing属性的作用',
                'dn': 'CSS盒模型包括内容、内边距、边框和外边距。box-sizing控制盒模型类型：content-box(默认)只包括内容区域，border-box包括内容、内边距和边框，更易于布局。',
                'difficulty': '简单'
            },
            {
                'wt': 'Vue的响应式原理是什么？Vue2和Vue3有何区别？',
                'dn': 'Vue2使用Object.defineProperty劫持对象属性。Vue3使用Proxy代理整个对象，可检测属性添加/删除、监听数组变化、性能更好，并采用Composition API提升逻辑复用性。',
                'difficulty': '中等'
            },
            {
                'wt': '如何实现高性能的大型列表组件？',
                'dn': '实现思路：虚拟滚动(只渲染可视区域)、数据分片与懒加载、DOM回收与复用、节流优化滚动事件、Web Workers处理计算、requestAnimationFrame同步更新、transform代替top定位。',
                'difficulty': '困难'
            }
        ],
        '软件工程师': [
            {
                'wt': 'RESTful API的主要原则有哪些？',
                'dn': 'RESTful原则：资源导向、HTTP方法语义(GET/POST/PUT/DELETE)、无状态、统一接口、HATEOAS(超链接)、分层系统。',
                'difficulty': '简单'
            },
            {
                'wt': '什么是设计模式？请描述三种常用设计模式',
                'dn': '设计模式是解决软件设计常见问题的可复用方案。常用模式：1)单例模式：确保类只有一个实例；2)观察者模式：定义对象间一对多依赖；3)工厂模式：定义创建对象的接口，由子类决定实例化类型。',
                'difficulty': '中等'
            },
            {
                'wt': '如何设计高并发、高可用的微服务架构系统？',
                'dn': '微服务架构：服务发现(Consul/Eureka)、API网关、负载均衡、服务通信(同步/异步)、容错(熔断/降级/限流)、配置中心、分布式跟踪、监控告警、容器化、多中心部署。核心原则：无状态、幂等、异步化。',
                'difficulty': '困难'
            }
        ],
        '大模型工程师': [
            {
                'wt': 'Transformer架构中自注意力机制是什么？',
                'dn': '自注意力机制计算：将输入转为查询(Q)、键(K)、值(V)三组向量；计算Q与K的点积得到注意力分数；缩放并应用softmax；与V相乘得到加权输出。能捕捉长距离依赖关系。',
                'difficulty': '简单'
            },
            {
                'wt': '什么是RLHF？如何应用于大模型训练？',
                'dn': 'RLHF步骤：预训练语言模型；收集人类偏好数据；训练奖励模型；使用强化学习(PPO)微调模型最大化奖励得分。解决关键问题：构建偏好数据集、防止模型偏离、确保奖励模型准确性。',
                'difficulty': '中等'
            },
            {
                'wt': '如何设计大规模多模态模型的训练和推理系统？',
                'dn': '系统设计：统一backbone架构；分布式训练(数据并行+模型并行)；混合精度训练；内存优化(梯度检查点)；高效数据处理；量化和KV缓存优化推理；多级批处理和负载均衡；自动调优监控。',
                'difficulty': '困难'
            }
        ]
    }
    
    # 插入所有问题
    for position in positions:  
        for question in questions_by_position[position]:
            conn.execute(
                'INSERT INTO mstk (wt, dn, gw, difficulty) VALUES (?, ?, ?, ?)',
                (question['wt'], question['dn'], position, question['difficulty'])
            )

# 导入问答解析模块
try:
    # 尝试直接导入
    from parse_answers import parse_answers, save_answers_to_file
    print("成功导入问答解析模块")
except ImportError as e:
    # 尝试相对路径导入
    try:
        parse_answers_path = os.path.join(os.path.dirname(__file__), 'parse_answers.py')
        if os.path.exists(parse_answers_path):
            print(f"问答解析模块文件存在于: {parse_answers_path}")
            # 使用importlib导入
            import importlib.util
            spec = importlib.util.spec_from_file_location("parse_answers", parse_answers_path)
            parse_answers_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(parse_answers_module)
            parse_answers = parse_answers_module.parse_answers
            save_answers_to_file = parse_answers_module.save_answers_to_file
            print("通过路径导入问答解析模块成功")
        else:
            print(f"问答解析模块文件不存在: {parse_answers_path}")
            raise ImportError(f"无法找到parse_answers.py文件: {parse_answers_path}")
    except Exception as inner_e:
        print(f"导入问答解析模块失败: {str(inner_e)}")
        print("将使用内置的问答解析函数")
        
        # 这里可以定义内置的解析函数作为备用
        # def parse_answers(...):
        #    ...
        # def save_answers_to_file(...):
        #    ...

@app.route('/')
def index():
    return render_template('index.html', 
                         xfyun_appid=app.config['XFYUN_APPID'],
                         xfyun_api_key=app.config['XFYUN_API_KEY'])

@app.route('/start_interview', methods=['POST'])
def start_interview():
    try:
        # 创建面试会话
        session_id = str(uuid.uuid4())
        
        # 获取职位信息
        position = request.json.get('position', '软件工程师')
        
        # 从数据库中随机抽取与职位相关的3个问题
        conn = get_db_connection()
        # 按难度不同抽取问题(简单、中等、困难各一题)
        difficulties = ['简单', '中等', '困难']
        questions = []
        
        for difficulty in difficulties:
            cursor = conn.execute(
                'SELECT id, wt, dn, difficulty FROM mstk WHERE gw = ? AND difficulty = ? ORDER BY RANDOM() LIMIT 1',
                (position, difficulty)
            )
            question = cursor.fetchone()
            if question:
                questions.append({
                    'id': question['id'],
                    'question': question['wt'],
                    'difficulty': question['difficulty'],
                    'reference_answer': question['dn']
                })
        
        conn.close()
        
        # 如果没有找到足够的问题，给出提示
        if len(questions) == 0:
            return jsonify({'error': f'数据库中没有找到与"{position}"相关的面试题'}), 404
        
        # 构建面试数据JSON
        interview_data = json.dumps({
            'questions': questions
        }, ensure_ascii=False)
        
        # 存储面试数据
        session_data = {
            'position': position,
            'interview_data': interview_data,
            'user_answers': {},
            'report': None
        }
        
        interview_sessions[session_id] = session_data
        # 立即保存会话数据到文件
        save_session_to_file(session_id, session_data)
        
        return jsonify({
            'session_id': session_id,
            'interview_data': interview_data
        })
        
    except Exception as e:
        print(f"创建面试会话失败: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    try:
        session_id = request.json.get('session_id')
        question_id = request.json.get('question_id')
        answer = request.json.get('answer')
        
        if not session_id or not question_id or not answer:
            return jsonify({'error': '缺少必要参数'}), 400
            
        # 获取会话数据，优先从内存获取，不存在则从文件加载
        session_data = get_session_data(session_id)
        if not session_data:
            return jsonify({'error': '面试会话不存在'}), 404
            
        # 获取问题内容和问题映射
        interview_data = json.loads(session_data['interview_data'])
        question_text = None
        question_map = {}  # 问题ID到问题文本的映射
        
        # 首先从当前面试的问题列表中获取映射
        for q in interview_data['questions']:
            q_id = str(q['id'])
            question_map[q_id] = q['question']
            if q_id == str(question_id):
                question_text = q['question']
        
        # 创建会话目录（如果不存在）
        session_dir = os.path.join(UPLOAD_FOLDER, session_id)
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
            
        # 解析回答文本，提取所有问题的回答
        print("解析回答文本...")
        try:
            all_answers = parse_answers(answer, question_id, interview_data)
        except Exception as parse_error:
            print(f"解析回答文本失败: {str(parse_error)}")
            all_answers = {str(question_id): answer}
        
        # 获取当前问题的解析回答
        parsed_answer = all_answers.get(str(question_id), answer)
        
        # 生成时间戳
        timestamp = int(time.time())
        
        # 保存原始文本文件
        text_filename = f"question_{question_id}_{timestamp}.txt"
        text_path = os.path.join(session_dir, text_filename)
        
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(f"原始识别文本：\n{answer}\n\n")
            f.write(f"问题：{question_text}\n\n")
            f.write(f"解析后的回答：\n{parsed_answer}\n")
        
        # 保存当前问题的问答对
        qa_filename = f"qa_{question_id}_{timestamp}.txt"
        qa_path = os.path.join(session_dir, qa_filename)
        
        with open(qa_path, 'w', encoding='utf-8') as f:
            f.write(f"问题：{question_text}\n\n")
            f.write(f"回答：{parsed_answer}\n")
        
        print(f"保存问答对文件: {qa_path}")  # 调试信息
        
        # 确保问题ID是字符串类型
        str_question_id = str(question_id)
        
        # 更新会话数据结构
        if 'files' not in session_data:
            session_data['files'] = {}
            
        if str_question_id not in session_data['files']:
            session_data['files'][str_question_id] = []
            
        file_entry = {
            'text_path': text_path,
            'qa_path': qa_path,
            'timestamp': timestamp,
            'original_text': answer,
            'parsed_answer': parsed_answer
        }
        
        session_data['files'][str_question_id].append(file_entry)
        
        # 同时更新用户回答
        if 'user_answers' not in session_data:
            session_data['user_answers'] = {}
        
        session_data['user_answers'][str_question_id] = parsed_answer
        
        # 如果提取到了多个问题的回答，保存完整问答对
        all_qa_path = None
        if len(all_answers) > 1:
            # 尝试从数据库中获取所有问题的信息，补充问题映射
            try:
                conn = get_db_connection()
                for q_num in all_answers.keys():
                    if q_num not in question_map:
                        cursor = conn.execute('SELECT wt FROM mstk WHERE id = ?', (q_num,))
                        question = cursor.fetchone()
                        if question:
                            question_map[q_num] = question['wt']
                conn.close()
            except Exception as e:
                print(f"获取额外问题内容时出错: {str(e)}")
            
            all_qa_path = save_answers_to_file(UPLOAD_FOLDER, session_id, all_answers, question_map, timestamp)
            
            # 为其他问题也保存单独的问答对文件
            for q_num, ans in all_answers.items():
                if q_num != str(question_id):
                    # 查找对应的问题ID
                    other_q_id = None
                    other_q_text = None
                    for q in interview_data['questions']:
                        if str(q['id']) == q_num:
                            other_q_id = q['id']
                            other_q_text = q['question']
                            break
                    
                    if other_q_id is not None:
                        # 为其他问题创建问答对文件
                        other_qa_filename = f"qa_{other_q_id}_{timestamp}.txt"
                        other_qa_path = os.path.join(session_dir, other_qa_filename)
                        
                        with open(other_qa_path, 'w', encoding='utf-8') as f:
                            f.write(f"问题：{other_q_text}\n\n")
                            f.write(f"回答：{ans}\n")
                        
                        # 更新会话数据
                        if other_q_id not in session_data['files']:
                            session_data['files'][other_q_id] = []
                            
                        other_file_entry = {
                            'qa_path': other_qa_path,
                            'timestamp': timestamp,
                            'original_text': answer,
                            'parsed_answer': ans
                        }
                        
                        session_data['files'][other_q_id].append(other_file_entry)
                        
                        # 更新用户回答
                        session_data['user_answers'][other_q_id] = ans
        
        # 立即保存更新后的会话数据到文件
        save_session_to_file(session_id, session_data)
        
        return jsonify({
            'success': True,
            'qa_path': qa_path,
            'all_answers': all_answers if len(all_answers) > 1 else None,
            'all_qa_path': all_qa_path,
            'question_map': question_map  # 添加问题映射
        })
        
    except Exception as e:
        print(f"提交回答出错: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/save_video', methods=['POST'])
def save_video():
    try:
        print("开始处理保存视频请求...")
        session_id = request.json.get('session_id')
        question_id = request.json.get('question_id')
        video_data = request.json.get('video_data')  # base64编码的视频数据
        answer_text = request.json.get('answer_text')  # 语音识别的文本结果
        
        # 确保问题ID是字符串
        str_question_id = str(question_id)
        
        # 输出请求基本信息（不包含视频数据本身）
        print(f"请求参数: session_id={session_id}, question_id={str_question_id}, 文本长度={len(answer_text) if answer_text else 0}")
        
        if not session_id or not question_id or not video_data or not answer_text:
            error_msg = f"缺少必要参数: session_id={bool(session_id)}, question_id={bool(question_id)}, video_data={'有' if video_data else '无'}, answer_text={'有' if answer_text else '无'}"
            print(error_msg)
            return jsonify({'error': error_msg}), 400
        
        # 获取会话数据，优先从内存获取，不存在则从文件加载
        session_data = get_session_data(session_id)
        if not session_data:
            print(f"面试会话不存在: {session_id}，尝试恢复会话")
            # 创建一个新的会话数据结构
            session_data = {
                'position': '未知职位',
                'interview_data': '{"questions":[]}',
                'user_answers': {},
                'report': None,
                'files': {},
                'recovered': True  # 标记为恢复的会话
            }
            interview_sessions[session_id] = session_data
            save_session_to_file(session_id, session_data)
            print(f"已创建恢复会话: {session_id}")
        
        # 创建会话目录
        session_dir = os.path.join(UPLOAD_FOLDER, session_id)
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
            print(f"创建会话目录: {os.path.abspath(session_dir)}")
        
        # 保存视频文件
        try:
            # 从base64字符串中提取视频数据
            print("解码视频数据...")
            video_base64 = video_data.split(',')[1] if ',' in video_data else video_data
            
            try:
                video_data_decoded = base64.b64decode(video_base64)
                print(f"视频数据解码成功，大小: {len(video_data_decoded)/1024/1024:.2f} MB")
            except Exception as decode_error:
                error_msg = f"视频数据解码失败: {str(decode_error)}"
                print(error_msg)
                traceback.print_exc()
                return jsonify({'error': error_msg}), 400
            
            # 生成文件名（使用时间戳避免重名）
            timestamp = int(time.time())
            video_filename = f"question_{question_id}_{timestamp}.mp4"
            video_path = os.path.join(session_dir, video_filename)
            
            # 写入视频文件
            print(f"正在保存视频到: {os.path.abspath(video_path)}")
            with open(video_path, 'wb') as f:
                f.write(video_data_decoded)
            
            print(f"视频文件保存成功: {os.path.getsize(video_path)/1024/1024:.2f} MB")
            
            # 获取问题内容和所有问题的映射
            try:
                interview_data = json.loads(session_data['interview_data'])
                question_text = None
                question_map = {}  # 问题ID到问题文本的映射
                
                # 首先从当前面试的问题列表中获取映射
                for q in interview_data['questions']:
                    q_id = str(q['id'])
                    question_map[q_id] = q['question']
                    if q_id == str(question_id):
                        question_text = q['question']
                        
                # 如果没有找到问题文本，使用默认值
                if not question_text:
                    question_text = f"问题 {question_id}"
            except Exception as e:
                print(f"获取问题内容失败: {str(e)}")
                question_text = f"问题 {question_id}"
                question_map = {str(question_id): question_text}
            
            # 解析回答文本，提取所有问题的回答
            print("解析回答文本...")
            try:
                all_answers = parse_answers(answer_text, question_id, interview_data)
            except Exception as parse_error:
                print(f"解析回答文本失败: {str(parse_error)}")
                all_answers = {str(question_id): answer_text}
            
            # 获取当前问题的解析回答
            parsed_answer = all_answers.get(str(question_id), answer_text)
            
            # 保存原始文本文件
            text_filename = f"question_{question_id}_{timestamp}.txt"
            text_path = os.path.join(session_dir, text_filename)
            
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(f"原始识别文本：\n{answer_text}\n\n")
                f.write(f"问题：{question_text}\n\n")
                f.write(f"解析后的回答：\n{parsed_answer}\n")
            
            # 保存当前问题的问答对
            qa_filename = f"qa_{question_id}_{timestamp}.txt"
            qa_path = os.path.join(session_dir, qa_filename)
            
            with open(qa_path, 'w', encoding='utf-8') as f:
                f.write(f"问题：{question_text}\n\n")
                f.write(f"回答：{parsed_answer}\n")
            
            print(f"保存问答对文件: {qa_path}")  # 调试信息
            
            # 确保问题ID是字符串类型
            str_question_id = str(question_id)
            
            # 更新会话数据结构
            if 'files' not in session_data:
                session_data['files'] = {}
                
            if str_question_id not in session_data['files']:
                session_data['files'][str_question_id] = []
                
            file_entry = {
                'video_path': video_path,
                'text_path': text_path,
                'qa_path': qa_path,
                'timestamp': timestamp,
                'original_text': answer_text,
                'parsed_answer': parsed_answer
            }
            
            session_data['files'][str_question_id].append(file_entry)
            
            # 同时更新用户回答
            if 'user_answers' not in session_data:
                session_data['user_answers'] = {}
            
            session_data['user_answers'][str_question_id] = parsed_answer
            
            # 如果提取到了多个问题的回答，保存完整问答对
            all_qa_path = None
            if len(all_answers) > 1:
                # 尝试从数据库中获取所有问题的信息，补充问题映射
                try:
                    conn = get_db_connection()
                    for q_num in all_answers.keys():
                        if q_num not in question_map:
                            cursor = conn.execute('SELECT wt FROM mstk WHERE id = ?', (q_num,))
                            question = cursor.fetchone()
                            if question:
                                question_map[q_num] = question['wt']
                    conn.close()
                except Exception as e:
                    print(f"获取额外问题内容时出错: {str(e)}")
                
                all_qa_path = save_answers_to_file(session_dir, session_id, all_answers, question_map, timestamp)
                
                # 为其他问题也保存单独的问答对文件
                for q_num, ans in all_answers.items():
                    if q_num != str(question_id):
                        # 查找对应的问题ID
                        other_q_id = None
                        other_q_text = None
                        for q in interview_data.get('questions', []):
                            if str(q['id']) == q_num:
                                other_q_id = q['id']
                                other_q_text = q['question']
                                break
                        
                        if other_q_id is not None:
                            # 为其他问题创建问答对文件
                            other_qa_filename = f"qa_{other_q_id}_{timestamp}.txt"
                            other_qa_path = os.path.join(session_dir, other_qa_filename)
                            
                            with open(other_qa_path, 'w', encoding='utf-8') as f:
                                f.write(f"问题：{other_q_text}\n\n")
                                f.write(f"回答：{ans}\n")
                            
                            # 更新会话数据
                            if other_q_id not in session_data['files']:
                                session_data['files'][other_q_id] = []
                                
                            other_file_entry = {
                                'qa_path': other_qa_path,
                                'timestamp': timestamp,
                                'original_text': answer_text,
                                'parsed_answer': ans
                            }
                            
                            session_data['files'][other_q_id].append(other_file_entry)
                            
                            # 更新用户回答
                            session_data['user_answers'][other_q_id] = ans
            
            # 添加：进行面部表情分析
            emotion_analysis_result = None
            emotion_path = None
            overall_emotion = None
            
            # 判断是否跳过面部表情分析（面部表情分析可能会消耗大量资源）
            skip_emotion_analysis = request.json.get('skip_emotion_analysis', False)
            
            if FACE_EMOTION_AVAILABLE and not skip_emotion_analysis:
                try:
                    print(f"开始进行面部表情分析: {video_path}")
                    analyzer = FaceEmotionAnalyzer()
                    # 使用较高的采样率以确保准确性，但不要太低以避免性能问题
                    analysis_result = analyzer.analyze_video(video_path, session_dir, sample_rate=30)
                    
                    emotion_path = analysis_result['output_path']
                    
                    # 保存详细的分析结果
                    emotion_analysis_result = analysis_result['results']
                    
                    # 保存整体情绪分析结果
                    overall_emotion = {
                        'dominant_emotion': analysis_result.get('dominant_emotion', 'neutral'),
                        'dominant_emotion_cn': analysis_result.get('dominant_emotion_cn', '中性'),
                        'emotions': analysis_result.get('overall_emotions', {}),
                        'frames_with_face': analysis_result.get('frames_with_face', 0)
                    }
                    
                    # 将表情分析结果路径添加到会话数据中
                    file_entry['emotion_path'] = emotion_path
                    file_entry['emotion_analysis'] = emotion_analysis_result
                    file_entry['overall_emotion'] = overall_emotion
                    
                    print(f"面部表情分析完成，结果保存在: {emotion_path}")
                    print(f"主要表情: {overall_emotion['dominant_emotion_cn']}")
                except Exception as e:
                    print(f"面部表情分析失败: {str(e)}")
                    traceback.print_exc()
                    # 不要因为表情分析失败而中断整个保存过程
            else:
                if skip_emotion_analysis:
                    print("用户选择跳过面部表情分析")
                else:
                    print("面部表情分析功能不可用")
            
            # 立即保存更新后的会话数据到文件
            save_session_to_file(session_id, session_data)
            
            print("视频和文本保存成功，准备返回结果")
            return jsonify({
                'success': True,
                'video_path': video_path,
                'text_path': text_path,
                'qa_path': qa_path,
                'original_text': answer_text,
                'parsed_answer': parsed_answer,
                'all_answers': all_answers if len(all_answers) > 1 else None,
                'all_qa_path': all_qa_path,
                'question_map': question_map,  # 添加问题映射
                'emotion_path': emotion_path,  # 添加表情分析结果路径
                'emotion_analysis': emotion_analysis_result,  # 添加表情分析结果
                'overall_emotion': overall_emotion  # 添加整体情绪分析结果
            })
            
        except Exception as e:
            error_msg = f"保存视频失败: {str(e)}"
            print(error_msg)
            traceback.print_exc()  # 打印详细的堆栈跟踪
            return jsonify({'error': error_msg}), 500
        
    except Exception as e:
        error_msg = f"处理请求失败: {str(e)}"
        print(error_msg)
        traceback.print_exc()  # 打印详细的堆栈跟踪
        return jsonify({'error': error_msg}), 500

@app.route('/generate_report', methods=['POST']) 
def generate_report():
    try:
        session_id = request.json.get('session_id')
        
        if not session_id:
            return jsonify({'error': '缺少会话ID'}), 400
            
        # 获取会话数据，优先从内存获取，不存在则从文件加载
        session_data = get_session_data(session_id)
        if not session_data:
            return jsonify({'error': '面试会话不存在'}), 404
        
        # 创建客户端连接
        client = ollama.Client()
        
        # 生成面试报告的提示
        prompt = f"""
        你是一位专业的面试评估专家。请根据以下信息生成一份面试报告：
        
        职位：{session_data['position']}
        
        面试数据：{session_data['interview_data']}
        
        用户回答：{session_data['user_answers']}
        
        请提供以下内容，使用Markdown格式：
        
        1. 首先，用"## 面试问题与回答"作为标题，列出每个问题和用户的回答
        2. 然后，用"## 评估分析"作为标题，对每个问题的回答进行评分（1-10分）和详细分析
        3. 接着，用"## 总体评价"作为标题，提供总体评价
        4. 再用"## 改进建议"作为标题，提供具体的改进建议
        5. 最后，用"## 总分"作为标题，给出最终得分（总分100分）
        
        请确保报告格式清晰，内容专业客观，评价公正。
        返回的整个内容应该是Markdown格式。
        """
        
        # 获取AI响应
        response = client.chat(model='llama3.2:latest', messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ])
        
        report = response['message']['content']
        
        # 存储报告
        session_data['report'] = report
        
        # 立即保存更新后的会话数据到文件
        save_session_to_file(session_id, session_data)
        
        return jsonify({
            'report': report
        })
        
    except Exception as e:
        print(f"生成面试报告失败: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # 获取用户输入
        user_input = request.json.get('message')
        
        if not user_input:
            return jsonify({'error': '没有收到消息'}), 400
            
        # 创建客户端连接
        client = ollama.Client()
        
        # 添加用户消息到历史
        messages = []
        messages.append({
            'role': 'user',
            'content': user_input
        })
        
        # 获取AI响应
        response = client.chat(model='llama3.2:latest', messages=messages)
        ai_response = response['message']['content']
        
        return jsonify({'response': ai_response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 添加新接口：获取问答对
@app.route('/get_qa_pairs', methods=['POST'])
def get_qa_pairs():
    try:
        session_id = request.json.get('session_id')
        question_id = request.json.get('question_id')
        check_all_questions_file = request.json.get('check_all_questions_file', False)
        
        print(f"获取问答对请求: session_id={session_id}, question_id={question_id}, check_all_questions_file={check_all_questions_file}")
        
        # 始终将问题ID转换为字符串（如果存在）
        str_question_id = str(question_id) if question_id is not None else None
        
        if not session_id:
            return jsonify({'error': '缺少会话ID'}), 400
        
        # 检查是否存在all_questions_*.txt文件
        if check_all_questions_file:
            session_dir = os.path.join(UPLOAD_FOLDER, session_id)
            session_sub_dir = os.path.join(session_dir, session_id)
            
            all_questions_files = []
            
            # 检查session_dir目录
            if os.path.exists(session_dir):
                for filename in os.listdir(session_dir):
                    if filename.startswith("all_questions_") and filename.endswith(".txt"):
                        all_questions_files.append(os.path.join(session_dir, filename))
                        print(f"在{session_dir}中找到all_questions文件: {filename}")
            
            # 如果在session_dir中没找到，检查session_sub_dir目录
            if not all_questions_files and os.path.exists(session_sub_dir):
                for filename in os.listdir(session_sub_dir):
                    if filename.startswith("all_questions_") and filename.endswith(".txt"):
                        all_questions_files.append(os.path.join(session_sub_dir, filename))
                        print(f"在{session_sub_dir}中找到all_questions文件: {filename}")
            
            has_all_questions_file = len(all_questions_files) > 0
            
            # 分析所有问题的回答状态
            all_answers_valid = {}
            if has_all_questions_file:
                # 获取最新的all_questions文件
                latest_file = sorted(all_questions_files, key=os.path.getmtime, reverse=True)[0]
                print(f"分析最新的all_questions文件: {latest_file}")
                
                try:
                    # 读取文件内容
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 使用分隔符拆分为问答对
                    qa_sections = content.split('-' * 50)
                    
                    # 分析每个问答对
                    for section in qa_sections:
                        section = section.strip()
                        if not section:
                            continue
                        
                        # 提取问题和回答
                        question_match = re.search(r'问题：(.*?)(?=\n\n回答：|\Z)', section, re.DOTALL)
                        answer_match = re.search(r'回答：(.*?)(?=\n\n|-{50}|\Z)', section, re.DOTALL)
                        
                        if question_match:
                            question_text = question_match.group(1).strip()
                            
                            # 尝试从数据库中找到对应的问题ID
                            question_id = None
                            conn = get_db_connection()
                            cursor = conn.execute('SELECT id FROM mstk WHERE wt = ?', (question_text,))
                            result = cursor.fetchone()
                            if result:
                                question_id = str(result['id'])
                            conn.close()
                            
                            # 如果找到了问题ID，检查回答是否有效
                            if question_id:
                                answer_text = ""
                                if answer_match:
                                    answer_text = answer_match.group(1).strip()
                                
                                # 判断回答是否有效（不为空）
                                is_valid = bool(answer_text)
                                all_answers_valid[question_id] = is_valid
                                
                                print(f"问题ID {question_id} 的回答{'有效' if is_valid else '无效'}")
                except Exception as e:
                    print(f"分析all_questions文件失败: {str(e)}")
                    traceback.print_exc()
            
            return jsonify({
                'has_all_questions_file': has_all_questions_file,
                'all_answers_valid': all_answers_valid
            })
        
        # 获取会话数据，优先从内存获取，不存在则从文件加载
        session_data = get_session_data(session_id)
        if not session_data:
            return jsonify({'error': '面试会话不存在'}), 404
        
        if 'files' not in session_data:
            print(f"会话 {session_id} 中没有问答记录")
            return jsonify({'qa_pairs': {}})
        
        # 打印所有可用的问题ID
        available_question_ids = list(session_data['files'].keys())
        print(f"会话中的所有问题ID: {available_question_ids}")
        
        # 打印问题ID的类型
        for qid in available_question_ids:
            print(f"问题ID类型: {qid} - {type(qid)}")
            
        # 确保所有问题ID都是字符串类型
        normalized_files = {}
        for qid, pairs in session_data['files'].items():
            normalized_files[str(qid)] = pairs
            
        # 更新session_data中的files
        session_data['files'] = normalized_files
        
        # 保存标准化后的会话数据
        save_session_to_file(session_id, session_data)
            
        if str_question_id and str_question_id in session_data['files']:
            # 返回特定问题的问答对
            qa_pairs = session_data['files'][str_question_id]
            print(f"返回问题 {str_question_id} 的问答对: {len(qa_pairs)} 条记录")
            return jsonify({'qa_pairs': {str_question_id: qa_pairs}})
        elif not question_id:
            # 返回所有问答对
            all_qa_pairs = {}
            for qid, pairs in session_data['files'].items():
                # 确保键是字符串
                all_qa_pairs[str(qid)] = pairs
            print(f"返回所有问答对: {len(all_qa_pairs)} 个问题")
            return jsonify({'qa_pairs': all_qa_pairs})
        else:
            print(f"问题ID {str_question_id} 不存在")
            return jsonify({'qa_pairs': {}})
            
    except Exception as e:
        error_msg = f"获取问答对失败: {str(e)}"
        print(f"错误: {error_msg}")
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

# 添加新接口：更新问答对
@app.route('/update_qa_pair', methods=['POST'])
def update_qa_pair():
    try:
        # 获取请求参数
        session_id = request.json.get('session_id')
        question_id = request.json.get('question_id')
        timestamp = request.json.get('timestamp')
        updated_answer = request.json.get('updated_answer')
        
        # 始终将问题ID转换为字符串
        str_question_id = str(question_id)
        
        print(f"收到更新问答对请求: session_id={session_id}, question_id={str_question_id}, timestamp={timestamp}")
        
        # 验证必要参数
        if not session_id or not question_id or timestamp is None or not updated_answer:
            missing_params = []
            if not session_id: missing_params.append('session_id')
            if not question_id: missing_params.append('question_id')
            if timestamp is None: missing_params.append('timestamp')
            if not updated_answer: missing_params.append('updated_answer')
            error_msg = f"缺少必要参数: {', '.join(missing_params)}"
            print(f"错误: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # 确保timestamp是整数
        try:
            timestamp = int(timestamp)
        except (ValueError, TypeError):
            error_msg = f"无效的时间戳格式: {timestamp}"
            print(f"错误: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # 获取会话数据，优先从内存获取，不存在则从文件加载
        session_data = get_session_data(session_id)
        if not session_data:
            error_msg = f"面试会话不存在: {session_id}"
            print(f"错误: {error_msg}")
            return jsonify({'error': error_msg}), 404
            
        # 验证问题ID是否存在
        if 'files' not in session_data:
            error_msg = "会话中没有问答记录"
            print(f"错误: {error_msg}")
            return jsonify({'error': error_msg}), 404
        
        # 打印所有可用的问题ID
        available_question_ids = list(session_data['files'].keys())
        print(f"会话中的所有问题ID: {available_question_ids}")
        
        # 检查字符串形式的问题ID是否存在
        if str_question_id not in session_data['files']:
            error_msg = f"问题ID不存在: {str_question_id}，可用的问题ID: {available_question_ids}"
            print(f"错误: {error_msg}")
            return jsonify({'error': error_msg}), 404
        
        # 查找对应的问答对
        qa_pair = None
        for pair in session_data['files'][str_question_id]:
            if pair['timestamp'] == timestamp:
                qa_pair = pair
                break
                
        if not qa_pair:
            error_msg = f"未找到指定的问答对: timestamp={timestamp}"
            print(f"错误: {error_msg}")
            return jsonify({'error': error_msg}), 404
            
        # 获取问题内容
        interview_data = json.loads(session_data['interview_data'])
        question_text = None
        for q in interview_data['questions']:
            if str(q['id']) == str_question_id:
                question_text = q['question']
                break
                
        if not question_text:
            error_msg = f"无法找到问题文本: question_id={str_question_id}"
            print(f"错误: {error_msg}")
            question_text = f"问题{str_question_id}"  # 使用默认问题文本
        
        # 更新问答对文件
        try:
            print(f"正在更新问答对文件: {qa_pair['qa_path']}")
            with open(qa_pair['qa_path'], 'w', encoding='utf-8') as f:
                f.write(f"问题：{question_text}\n\n")
                f.write(f"回答：{updated_answer}\n")
        except Exception as file_error:
            error_msg = f"更新问答对文件失败: {str(file_error)}"
            print(f"错误: {error_msg}")
            return jsonify({'error': error_msg}), 500
        
        # 更新会话数据
        qa_pair['parsed_answer'] = updated_answer
        print(f"更新问答对内存数据: timestamp={timestamp}")
        
        # 同时更新用户回答
        if 'user_answers' not in session_data:
            session_data['user_answers'] = {}
        session_data['user_answers'][str_question_id] = updated_answer
        print(f"更新用户回答: question_id={str_question_id}")
        
        # 更新all_questions_*.txt文件（如果存在）
        try:
            session_dir = os.path.join(UPLOAD_FOLDER, session_id)
            session_sub_dir = os.path.join(session_dir, session_id)
            all_questions_files = []
            
            # 查找session_dir中的所有all_questions_*.txt文件
            if os.path.exists(session_dir):
                for filename in os.listdir(session_dir):
                    if filename.startswith("all_questions_") and filename.endswith(".txt"):
                        all_questions_files.append(os.path.join(session_dir, filename))
            
            # 查找session_sub_dir中的所有all_questions_*.txt文件
            if os.path.exists(session_sub_dir):
                for filename in os.listdir(session_sub_dir):
                    if filename.startswith("all_questions_") and filename.endswith(".txt"):
                        all_questions_files.append(os.path.join(session_sub_dir, filename))
            
            print(f"找到 {len(all_questions_files)} 个all_questions文件")
            
            # 更新每个all_questions_*.txt文件
            for file_path in all_questions_files:
                print(f"正在更新问答汇总文件: {file_path}")
                
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 使用更精确的模式匹配问题和回答
                # 问题内容可能包含特殊字符，需要转义
                escaped_question = re.escape(question_text.strip())
                pattern = f"问题：{escaped_question}[\\s\\S]*?回答：([\\s\\S]*?)(?=\\n\\n-{{50}}|\\Z)"
                
                match = re.search(pattern, content)
                if match:
                    # 找到匹配的部分，进行替换
                    # 构造替换模式
                    replacement = f"问题：{question_text}\n\n回答：{updated_answer}"
                    
                    # 计算问题部分的开始位置和结束位置
                    start_pos = content.find(f"问题：{question_text}")
                    
                    if start_pos != -1:
                        # 查找下一个分隔符或文件结束
                        end_marker = "-" * 50
                        end_pos = content.find(end_marker, start_pos)
                        if end_pos == -1:
                            # 如果没有找到分隔符，使用文件结尾
                            end_pos = len(content)
                        
                        # 替换整个问答对
                        new_content = content[:start_pos] + replacement + content[end_pos:]
                        
                        # 写入更新后的内容
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        print(f"已更新文件: {file_path}")
                    else:
                        print(f"在文件中找到匹配的正则表达式，但无法确定精确位置")
                else:
                    print(f"在文件 {file_path} 中未找到匹配的问题: {question_text}")
                    # 输出文件内容的前100个字符以帮助调试
                    print(f"文件内容前100个字符: {content[:100]}")
            
        except Exception as all_q_error:
            print(f"更新all_questions文件失败，但不影响主要功能: {str(all_q_error)}")
            traceback.print_exc()
        
        # 立即保存更新后的会话数据到文件
        save_result = save_session_to_file(session_id, session_data)
        if not save_result:
            error_msg = "保存会话数据到文件失败"
            print(f"错误: {error_msg}")
            return jsonify({'error': error_msg}), 500
            
        print(f"问答对更新成功: session_id={session_id}, question_id={str_question_id}, timestamp={timestamp}")
        return jsonify({'success': True})
        
    except Exception as e:
        error_msg = f"更新问答对失败: {str(e)}"
        print(f"错误: {error_msg}")
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

# 添加一个定期保存会话数据的函数，可以通过定时器调用
def save_all_sessions():
    print("正在保存所有会话数据...")
    with session_lock:
        for session_id, session_data in interview_sessions.items():
            save_session_to_file(session_id, session_data)
    print("所有会话数据已保存")

# 在应用启动时加载所有会话数据
def load_all_sessions():
    if os.path.exists(SESSIONS_FOLDER):
        for filename in os.listdir(SESSIONS_FOLDER):
            if filename.endswith('.pickle'):
                session_id = filename[:-7]  # 去掉.pickle后缀
                session_data = load_session_from_file(session_id)
                if session_data:
                    interview_sessions[session_id] = session_data
        print(f"已加载 {len(interview_sessions)} 个会话数据")

# 在应用启动时初始化数据库和加载会话
with app.app_context():
    init_db()
    load_all_sessions()

# 添加一个接口用于读取all_questions文件内容（用于调试）
@app.route('/get_all_questions_content', methods=['POST'])
def get_all_questions_content():
    try:
        session_id = request.json.get('session_id')
        
        if not session_id:
            return jsonify({'error': '缺少会话ID'}), 400
            
        session_dir = os.path.join(UPLOAD_FOLDER, session_id)
        session_sub_dir = os.path.join(session_dir, session_id)
        all_questions_files = []
        
        # 查找session_dir中的所有all_questions_*.txt文件
        if os.path.exists(session_dir):
            for filename in os.listdir(session_dir):
                if filename.startswith("all_questions_") and filename.endswith(".txt"):
                    all_questions_files.append(os.path.join(session_dir, filename))
        
        # 查找session_sub_dir中的所有all_questions_*.txt文件
        if os.path.exists(session_sub_dir):
            for filename in os.listdir(session_sub_dir):
                if filename.startswith("all_questions_") and filename.endswith(".txt"):
                    all_questions_files.append(os.path.join(session_sub_dir, filename))
        
        if not all_questions_files:
            return jsonify({'error': '未找到all_questions文件'}), 404
            
        # 获取最新的all_questions文件
        latest_file = sorted(all_questions_files, key=os.path.getmtime, reverse=True)[0]
        
        # 读取文件内容
        with open(latest_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 解析问答对
        qa_pairs = []
        sections = content.split('-' * 50)
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # 提取问题和回答
            question_match = re.search(r'问题：(.*?)(?=\n\n回答：|\Z)', section, re.DOTALL)
            answer_match = re.search(r'回答：(.*?)(?=\n\n|-{50}|\Z)', section, re.DOTALL)
            
            if question_match:
                question = question_match.group(1).strip()
                answer = answer_match.group(1).strip() if answer_match else ""
                
                qa_pairs.append({
                    'question': question,
                    'answer': answer
                })
        
        return jsonify({
            'file_path': latest_file,
            'file_content': content,
            'qa_pairs': qa_pairs
        })
        
    except Exception as e:
        error_msg = f"获取all_questions文件内容失败: {str(e)}"
        print(f"错误: {error_msg}")
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    # 关闭调试模式，避免自动重载导致会话丢失
    app.run(debug=False, host='0.0.0.0', port=5333) 