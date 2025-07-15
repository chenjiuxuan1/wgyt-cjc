from flask import Flask, jsonify, request, send_from_directory, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import config
import json
import time
import os
import requests

app = Flask(__name__)
# 简化的CORS配置
CORS(app, resources={r"/*": {"origins": "*"}})

# 配置数据库连接
app.config.from_object(config)
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'] + '?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)

class Astock(db.Model):
    __tablename__ = 'gsjbxx_wz'
    id = db.Column(db.String(255), primary_key=True)
    firm_eid = db.Column(db.Text)
    C3 = db.Column(db.Text)
    C4 = db.Column(db.Text)
    C5 = db.Column(db.Text)
    C6 = db.Column(db.Text)
    C7 = db.Column(db.Text)
    C8 = db.Column(db.Text)
    C9 = db.Column(db.Text)
    C10 = db.Column(db.Text)
    C11 = db.Column(db.Text)
    C12 = db.Column(db.Integer)
    C13 = db.Column(db.Text)
    C14 = db.Column(db.Text)
    C30 = db.Column(db.Float)
    C31 = db.Column(db.Float)
    C66 = db.Column(db.Date)

# 添加岗位信息模型
class JobInfo(db.Model):
    __tablename__ = '岗位信息'
    __bind_key__ = 'zhaoping'
    __table_args__ = {'extend_existing': True}
    
    岗位名称 = db.Column(db.Text, primary_key=True)  # 使用岗位名称作为主键
    岗位一级分类 = db.Column(db.Text)
    岗位二级分类 = db.Column(db.Text)
    工作地点 = db.Column(db.Text)
    工作省份 = db.Column(db.Text)
    岗位薪资 = db.Column(db.Text)
    企业名称 = db.Column(db.Text)
    经验要求 = db.Column(db.Text)
    学历要求 = db.Column(db.Text)
    岗位技能需求 = db.Column(db.Text)
    企业类型 = db.Column(db.Text)
    企业融资状况 = db.Column(db.Text)
    企业规模 = db.Column(db.Text)

# 确保在应用上下文中初始化数据库
with app.app_context():
    try:
        db.create_all()
        print("数据库表已创建")
    except Exception as e:
        print(f"数据库初始化错误: {str(e)}")

@app.before_request
def before_request():
    request.start_time = time.time()
    print(f"\n{'='*50}")
    print(f"收到请求: {request.method} {request.path}")
    print(f"请求URL: {request.url}")
    print(f"请求参数: {request.args}")
    print(f"请求头: {dict(request.headers)}")
    print(f"请求体: {request.get_data(as_text=True)}")
    print(f"{'='*50}\n")

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        response.headers['X-Request-Duration'] = str(duration)
    
    # 完全开放的响应头
    origin = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE, PATCH, HEAD'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Expose-Headers'] = '*'
    response.headers['Access-Control-Max-Age'] = '86400'
    
    print(f"\n{'='*50}")
    print(f"响应状态: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应数据: {response.get_data(as_text=True)}")
    print(f"处理时间: {duration if hasattr(request, 'start_time') else 'N/A'} 秒")
    print(f"{'='*50}\n")
    return response

@app.route('/')
def serve_static():
    return send_from_directory('dist', 'index.html')

@app.route('/<path:path>')
def serve_files(path):
    if os.path.exists(os.path.join('dist', path)):
        return send_from_directory('dist', path)
    return jsonify({'status': 'error', 'message': '请求的资源不存在'}), 404

# 处理OPTIONS请求
@app.route('/api/company/search', methods=['OPTIONS'])
def handle_options():
    return '', 204

# 公司搜索API
@app.route('/api/company/search', methods=['GET'])
def search_company():
    try:
        print("\n开始处理搜索请求")
        print(f"完整URL: {request.url}")
        print(f"请求方法: {request.method}")
        print(f"请求参数: {request.args}")
        
        keyword = request.args.get('keyword', '')
        if not keyword:
            print("关键词为空")
            return jsonify({
                'status': 'error',
                'message': '搜索关键词不能为空',
                'companies': []
            }), 400
        
        print(f"搜索关键词: {keyword}")
        
        companies = db.session.query(
            Astock
        ).filter(
            Astock.C6.ilike(f'%{keyword}%'),  # 公司名称模糊匹配
            Astock.C30.between(106.2, 106.9),  # 重庆主城区经度范围
            Astock.C31.between(29.4, 29.9),    # 重庆主城区纬度范围
            Astock.C6.isnot(None),
            Astock.C30.isnot(None),
            Astock.C31.isnot(None)
        ).all()
        
        print(f"查询到 {len(companies)} 条结果")
        
        results = []
        seen = set()
        
        for company in companies:
            try:
                company_name = company.C6.strip() if company.C6 else ''
                if not company_name or company_name in seen:
                    continue
                seen.add(company_name)
                
                data = {
                    'name': company_name,
                    'value': [
                        float(company.C30) if company.C30 else 0,
                        float(company.C31) if company.C31 else 0
                    ],
                    'type': company.C10.strip() if company.C10 else '未知类型',
                    'C3': company.C3.strip() if company.C3 else '未知',
                    'C11': company.C11.strip() if company.C11 else '未知',
                    'C14': company.C14.strip() if company.C14 else '未上市',
                    'C13': company.C13.strip() if company.C13 else '暂无描述',
                    'firm_eid': company.firm_eid.strip() if company.firm_eid else ''
                }
                
                if all(isinstance(x, (int, float)) for x in data['value']):
                    results.append(data)
                    print(f"添加结果: {data['name']}, 位置: {data['value']}")
            except Exception as e:
                print(f"处理公司数据时出错: {str(e)}, 公司: {company.C6 if company.C6 else 'Unknown'}")
                continue
        
        response = {
            'status': 'success',
            'companies': results
        }
        print(f"返回 {len(results)} 条有效结果")
        return jsonify(response)
        
    except Exception as e:
        print(f"搜索公司时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '搜索失败，请稍后重试',
            'error': str(e)
        }), 500

# 处理岗位推荐的OPTIONS请求
@app.route('/api/jobs/recommend', methods=['OPTIONS'])
def handle_jobs_recommend_options():
    return '', 204

# 岗位推荐API
@app.route('/api/jobs/recommend', methods=['POST'])
def recommend_jobs():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求数据不能为空',
                'data': []
            }), 400
        
        params = data.get('params', {})
        weights = data.get('weights', {})
        
        # 构建查询条件
        query = db.session.query(JobInfo)
        
        # 添加筛选条件
        if params.get('city'):
            query = query.filter(JobInfo.工作地点.ilike(f"%{params['city']}%"))
        if params.get('education'):
            query = query.filter(JobInfo.学历要求.ilike(f"%{params['education']}%"))
        if params.get('experience'):
            query = query.filter(JobInfo.经验要求.ilike(f"%{params['experience']}%"))
        if params.get('position'):
            query = query.filter(db.or_(
                JobInfo.岗位名称.ilike(f"%{params['position']}%"),
                JobInfo.岗位一级分类.ilike(f"%{params['position']}%"),
                JobInfo.岗位二级分类.ilike(f"%{params['position']}%")
            ))
        if params.get('companyType'):
            query = query.filter(JobInfo.企业类型.ilike(f"%{params['companyType']}%"))
        if params.get('scale'):
            query = query.filter(JobInfo.企业规模.ilike(f"%{params['scale']}%"))
        
        # 限制查询结果数量
        jobs = query.limit(30).all()
        
        # 处理结果
        results = []
        for job in jobs:
            try:
                # 计算匹配分数
                match_score = 0
                total_weight = 0
                
                # 根据各个条件计算匹配度
                if params.get('city') and weights.get('city'):
                    total_weight += weights['city']
                    if job.工作地点 and params['city'] in job.工作地点:
                        match_score += weights['city']
                
                if params.get('education') and weights.get('education'):
                    total_weight += weights['education']
                    if job.学历要求 and params['education'] in job.学历要求:
                        match_score += weights['education']
                
                if params.get('experience') and weights.get('experience'):
                    total_weight += weights['experience']
                    if job.经验要求 and params['experience'] in job.经验要求:
                        match_score += weights['experience']
                
                if params.get('position') and weights.get('position'):
                    total_weight += weights['position']
                    position_match = any([
                        job.岗位名称 and params['position'] in job.岗位名称,
                        job.岗位一级分类 and params['position'] in job.岗位一级分类,
                        job.岗位二级分类 and params['position'] in job.岗位二级分类
                    ])
                    if position_match:
                        match_score += weights['position']
                
                if params.get('companyType') and weights.get('companyType'):
                    total_weight += weights['companyType']
                    if job.企业类型 and params['companyType'] in job.企业类型:
                        match_score += weights['companyType']
                
                if params.get('scale') and weights.get('scale'):
                    total_weight += weights['scale']
                    if job.企业规模 and params['scale'] in job.企业规模:
                        match_score += weights['scale']
                
                # 计算最终匹配度
                final_score = (match_score / total_weight * 100) if total_weight > 0 else 0
                
                # 构建返回数据
                job_data = {
                    'position': job.岗位名称 or '未知职位',
                    'company': job.企业名称 or '未知公司',
                    'city': job.工作地点 or '未知地区',
                    'salary': job.岗位薪资 or '薪资面议',
                    'education': job.学历要求 or '学历不限',
                    'experience': job.经验要求 or '经验不限',
                    'companyType': job.企业类型 or '未知类型',
                    'scale': job.企业规模 or '规模未知',
                    'matchScore': final_score,
                    'category': {
                        'level1': job.岗位一级分类 or '未分类',
                        'level2': job.岗位二级分类 or '未分类'
                    }
                }
                
                results.append(job_data)
                
            except Exception as e:
                continue
        
        # 按匹配度排序并只返回前15个结果
        results.sort(key=lambda x: x['matchScore'], reverse=True)
        results = results[:15]
        
        response = {
            'code': 200,
            'message': '查询成功',
            'data': results
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': '推荐失败，请稍后重试',
            'error': str(e)
        }), 500

# 处理岗位预警的OPTIONS请求
@app.route('/api/jobs/alert/check', methods=['OPTIONS'])
def handle_jobs_alert_options():
    return '', 204

# 代理转发API请求
@app.route('/api/v1/workspace/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy_workspace_request(path):
    try:
        print(f"\n{'='*50}")
        print(f"收到工作空间代理请求:")
        print(f"路径: {path}")
        print(f"方法: {request.method}")
        print(f"请求头: {dict(request.headers)}")
        print(f"请求数据: {request.get_data(as_text=True)}")
        
        # 构建目标URL
        target_url = f'http://localhost:3001/api/v1/workspace/{path}'
        print(f"转发到目标URL: {target_url}")
        
        # 获取请求数据
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # 转发请求头
        headers = {
            key: value for key, value in request.headers.items()
            if key.lower() not in ['host', 'content-length']
        }
        
        # 发送请求到目标服务器
        response = requests.request(
            method=request.method,
            url=target_url,
            json=data if request.is_json else None,
            data=None if request.is_json else data,
            headers=headers,
            params=request.args,
            timeout=60,
            verify=False
        )
        
        print(f"目标服务器响应状态码: {response.status_code}")
        print(f"目标服务器响应头: {dict(response.headers)}")
        print(f"目标服务器响应内容: {response.text}")
        
        # 返回响应
        return (response.content, response.status_code, {
            key: value for key, value in response.headers.items()
            if key.lower() not in ['content-encoding', 'content-length', 'transfer-encoding']
        })
        
    except requests.RequestException as e:
        print(f"代理请求网络错误: {str(e)}")
        return jsonify({
            'error': str(e),
            'message': '代理请求网络错误',
            'type': 'network_error'
        }), 500
        
    except Exception as e:
        print(f"代理请求未知错误: {str(e)}")
        return jsonify({
            'error': str(e),
            'message': '代理请求未知错误',
            'type': 'unknown_error'
        }), 500

# 处理 OPTIONS 请求
@app.route('/api/v1/workspace/<path:path>', methods=['OPTIONS'])
def handle_workspace_options(path):
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
    return response

# 岗位预警API
@app.route('/api/jobs/alert/check', methods=['POST'])
def check_job_alerts():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求数据不能为空',
                'data': None
            }), 400
        
        conditions = data.get('conditions', {})
        threshold = data.get('threshold', 5)  # 默认阈值为5
        model_api_url = data.get('modelApiUrl')  # 从请求中获取模型API地址
        
        # 构建查询条件
        query = db.session.query(JobInfo)
        
        # 添加筛选条件
        if conditions.get('city'):
            query = query.filter(JobInfo.工作地点.ilike(f"%{conditions['city']}%"))
        if conditions.get('education'):
            query = query.filter(JobInfo.学历要求.ilike(f"%{conditions['education']}%"))
        if conditions.get('experience'):
            query = query.filter(JobInfo.经验要求.ilike(f"%{conditions['experience']}%"))
        if conditions.get('position'):
            query = query.filter(db.or_(
                JobInfo.岗位名称.ilike(f"%{conditions['position']}%"),
                JobInfo.岗位一级分类.ilike(f"%{conditions['position']}%"),
                JobInfo.岗位二级分类.ilike(f"%{conditions['position']}%")
            ))
        if conditions.get('companyType'):
            query = query.filter(JobInfo.企业类型.ilike(f"%{conditions['companyType']}%"))
        if conditions.get('scale'):
            query = query.filter(JobInfo.企业规模.ilike(f"%{conditions['scale']}%"))
        
        # 限制查询结果数量
        results = query.limit(15).all()
        
        # 处理结果
        jobs = []
        for job in results:
            job_data = {
                'position': job.岗位名称 or '未知职位',
                'company': job.企业名称 or '未知公司',
                'city': job.工作地点 or '未知地区',
                'salary': job.岗位薪资 or '薪资面议',
                'education': job.学历要求 or '学历不限',
                'experience': job.经验要求 or '经验不限',
                'companyType': job.企业类型 or '未知类型',
                'scale': job.企业规模 or '规模未知',
                'category': {
                    'level1': job.岗位一级分类 or '未分类',
                    'level2': job.岗位二级分类 or '未分类'
                }
            }
            jobs.append(job_data)
            
        # 如果提供了模型API地址，则发送数据进行分析
        if model_api_url:
            try:
                # 构建发送给大模型的数据
                model_data = {
                    'jobs': jobs,
                    'conditions': conditions,
                    'threshold': threshold
                }
                
                # 转发所有请求头
                headers = {key: value for key, value in request.headers.items()
                          if key.lower() not in ['host', 'content-length']}
                
                # 发送请求到指定的模型API
                model_response = requests.post(
                    model_api_url,
                    json=model_data,
                    headers=headers,
                    timeout=60,  # 增加超时时间到60秒
                    verify=False  # 忽略SSL证书验证
                )
                
                if model_response.status_code == 200:
                    model_result = model_response.json()
                    # 合并大模型的分析结果
                    response = {
                        'code': 200,
                        'message': '检查完成',
                        'data': {
                            'jobs': jobs,
                            'total': len(jobs),
                            'threshold': threshold,
                            'isTriggered': len(jobs) >= threshold,
                            'analysis': model_result
                        }
                    }
                else:
                    raise Exception(f"模型API返回错误: {model_response.status_code}")
            except Exception as e:
                print(f"大模型请求失败: {str(e)}")
                # 如果大模型请求失败，返回基本信息
                response = {
                    'code': 200,
                    'message': '检查完成（大模型分析未完成）',
                    'data': {
                        'jobs': jobs,
                        'total': len(jobs),
                        'threshold': threshold,
                        'isTriggered': len(jobs) >= threshold,
                        'error': str(e)
                    }
                }
        else:
            # 如果没有提供模型API地址，只返回基本信息
            response = {
                'code': 200,
                'message': '检查完成（未指定大模型API）',
                'data': {
                    'jobs': jobs,
                    'total': len(jobs),
                    'threshold': threshold,
                    'isTriggered': len(jobs) >= threshold
                }
            }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"岗位预警检查失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '预警检查失败，请稍后重试',
            'error': str(e)
        }), 500

# 处理路由规划的 OPTIONS 请求
@app.route('/api/route-planning', methods=['OPTIONS'])
def handle_route_planning_options():
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    return response

# 路由规划代理
@app.route('/api/route-planning', methods=['POST'])
def route_planning_proxy():
    try:
        print("\n接收到路由规划请求:")
        print(f"请求头: {dict(request.headers)}")
        print(f"原始数据: {request.get_data(as_text=True)}")
        
        data = request.get_json()
        print(f"解析后的JSON数据: {data}")
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': '请提供问题内容'
            }), 400

        if 'question' not in data:
            return jsonify({
                'status': 'error',
                'message': '请求数据必须包含question字段'
            }), 400

        # 转发到路线规划服务器
        try:
            session = requests.Session()
            print(f"\n转发请求到路由规划服务器:")
            print(f"URL: http://127.0.0.1:5123/api/route-planning")
            print(f"发送数据: {data}")
            
            response = session.post(
                'http://127.0.0.1:5123/api/route-planning',
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            
            print(f"\n收到服务器响应:")
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            # 检查响应状态
            try:
                result = response.json()
                # 处理400状态码（客户端错误）
                if response.status_code == 400:
                    return jsonify({
                        'status': 'error',
                        'message': result.get('error', '请提供有效的起点和终点')
                    }), 400
                # 处理200状态码（成功）
                elif response.status_code == 200:
                    if isinstance(result, dict) and 'error' in result:
                        return jsonify({
                            'status': 'error',
                            'message': result['error']
                        }), 400
                    return jsonify({
                        'status': 'success',
                        'result': result.get('result', result)
                    }), 200
                # 处理其他状态码
                else:
                    return jsonify({
                        'status': 'error',
                        'message': result.get('error', f'服务器返回错误: {response.text}')
                    }), response.status_code
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': '服务器返回了无效的数据格式'
                }), 500
                
        except requests.exceptions.ConnectionError:
            return jsonify({
                'status': 'error',
                'message': '无法连接到路线规划服务器，请确保服务已启动'
            }), 503
        except requests.exceptions.Timeout:
            return jsonify({
                'status': 'error',
                'message': '服务器响应超时，请稍后重试'
            }), 504
        except Exception as e:
            print(f"处理请求时出错: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'处理请求时出错: {str(e)}'
            }), 500
            
    except Exception as e:
        print(f"请求处理失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'请求处理失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("\n启动Flask应用...")
    print("监听地址: 127.0.0.1:5173")
    print("调试模式: 开启")
    
    # 检查路由规划服务器是否可用
    try:
        session = requests.Session()
        test_response = session.post(
            'http://127.0.0.1:5123/api/route-planning',
            json={"question": "test"},
            timeout=30
        )
        # 修改检查逻辑，允许400状态码
        if test_response.status_code in [200, 400]:
            print("路由规划服务器连接正常")
        else:
            print(f"警告: 路由规划服务器响应异常，状态码: {test_response.status_code}")
    except requests.exceptions.ConnectionError:
        print("警告: 路由规划服务器未启动，请先运行 route_planning_server.py")
    except Exception as e:
        print(f"警告: 检查路由规划服务器时出现错误: {str(e)}")
    
    app.run(host='127.0.0.1', port=5173, debug=True)