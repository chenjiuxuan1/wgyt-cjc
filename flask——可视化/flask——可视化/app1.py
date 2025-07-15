from flask import Flask, render_template, send_from_directory, jsonify, request, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy
import config
from sqlalchemy import or_

# 创建 Flask 应用
app = Flask(__name__, 
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'static')),
    template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
)
app.debug = True  # 启用调试模式

# 加载配置
app.config.from_object(config)
print(app.config['SQLALCHEMY_DATABASE_URI'])
# 初始化数据库
db = SQLAlchemy(app)

# 定义模型
class URLData(db.Model):
    __tablename__ = 'url_data'
    fl_1 = db.Column(db.String(255))
    fl_2 = db.Column(db.String(255))
    title = db.Column(db.String(255))
    url = db.Column(db.String(255), primary_key=True)
    

# 创建数据库表
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """重定向到视频页面"""
    return redirect(url_for('show_video'))

@app.route('/video')
def show_video():
   try:
       # 检查模板文件是否存在
       template_path = os.path.join(app.template_folder, 'xxsp.html')
       if not os.path.exists(template_path):
           return f"模板文件不存在: {template_path}", 500
           
       # 定义分类映射
       categories = [
           {'id': 'home', 'name': '首页'},
           {'id': 'bigdata', 'name': '大数据'},
           {'id': 'ai', 'name': '人工智能'},
           {'id': 'software', 'name': '软件工程'},
           {'id': 'manufacturing', 'name': '智能制造'},
           {'id': 'repair', 'name': '家电维修'},
           {'id': 'service', 'name': '服务行业'}
       ]
       
       # 从数据库获取数据
       data_list = URLData.query.all()
       videos_by_category = {category['id']: [] for category in categories}
       
       # 文件名映射
       filename_map = {
           'static/测试1.mp4': '/static/测试.mp4',
           'static/测试2.mp4': '/static/测试2.mp4',
           'static/测试3.mp4': '/static/测试.mp4',
           'static/测试4.mp4': '/static/测试2.mp4',
           'static/测试5.mp4': '/static/测试.mp4',
           'static/测试6.mp4': '/static/测试2.mp4'
       }
       
       if data_list:
           for data in data_list:
               category = data.fl_1
               if category in videos_by_category:
                   # 使用映射表转换URL
                   video_url = filename_map.get(data.url, data.url)
                   if not video_url.startswith('/'):
                       video_url = f'/static/{video_url}'
                   
                   videos_by_category[category].append({
                       'url': video_url,
                       'title': data.title,
                   })
       
       return render_template('xxsp.html', 
                            categories=categories,
                            videos_by_category=videos_by_category)
   except Exception as e:
       print(f"错误: {str(e)}")
       return f"发生错误: {str(e)}", 500

@app.route('/get_videos/<category>/<subcategory>')
def get_videos(category, subcategory):
    try:
        # 一级分类映射
        category_mapping = {
            '首页': 'home',
            '大数据': 'bigdata',
            '人工智能': 'ai',
            '软件工程': 'software',
            '智能制造': 'manufacturing',
            '家电维修': 'repair',
            '服务行业': 'service'
        }
        
        # 每个一级分类下的二级分类映射（从1开始编号）
        subcategory_mapping = {
            '大数据': {
                'python': '1',
                '数据结构算法': '2',
                '数据采集': '3',
                'flask开发': '4',
                '其他': '5'
            },
            '人工智能': {
                '机器识别': '1',
                '机器学习': '2',
                '人工智能核心算法': '3',
                '其他': '4'
            },
            '软件工程': {
                'java': '1',
                '前端开发': '2',
                '软件测试': '3',
                'app开发': '4',
                '其他': '5'
            },
            '智能制造': {
                '物联网技术': '1',
                'c/c++': '2',
                '供应链管理': '3',
                '其他': '4'
            },
            '家电维修': {
                '简单维修': '1',
                '电器维修': '2',
                '其他': '3'
            },
            '服务行业': {
                '自我修养': '1',
                '接待与运维': '2',
                '其他': '3'
            }
        }
        
        # 如果是首页，返回所有视频
        if category == '首页':
            videos = URLData.query.all()
        else:
            db_category = category_mapping.get(category)
            if not db_category:
                return jsonify({'error': '无效的分类'}), 400
                
            if subcategory == '全部推荐':
                # 如果是全部推荐，只按一级分类查询
                videos = URLData.query.filter_by(fl_1=db_category).all()
            else:
                # 获取当前分类的二级分类映射
                category_subcategories = subcategory_mapping.get(category, {})
                # 获取二级分类代码
                db_subcategory = category_subcategories.get(subcategory)
                if not db_subcategory:
                    return jsonify({'error': '无效的二级分类'}), 400
                    
                # 按一级和二级分类查询
                videos = URLData.query.filter_by(
                    fl_1=db_category,
                    fl_2=db_subcategory
                ).all()
        
        # 转换结果
        video_list = []
        for video in videos:
            try:
                video_list.append({
                    'url': video.url,
                    'title': video.title,
                    'category': get_category_name(video.fl_1)
                })
            except AttributeError as e:
                print(f"视频数据缺少必要字段: {str(e)}")
                continue
                
        return jsonify({'videos': video_list})
            
    except Exception as e:
        print(f"详细错误信息: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 反向查找函数，根据值获取键
def get_key_by_value(mapping, value):
    for key, val in mapping.items():
        if val == value:
            return key
    return '未知'  # 如果未找到，返回 None 或其他默认值

@app.route('/search')
def search_videos():
    try:
        keyword = request.args.get('keyword', '')
        if not keyword:
            return jsonify({'videos': []})
        
        # 分类代码到显示名称的映射
        category_mapping = {
            'bigdata': '大数据',
            'ai': '人工智能',
            'software': '软件工程',
            'manufacturing': '智能制造',
            'repair': '家电维修',
            'service': '服务行业'
        }
        
        # 创建反向映射（显示名称到代码）
        reverse_mapping = {v: k for k, v in category_mapping.items()}
        
        # 使用 or_ 进行模糊搜索，匹配：
        # 1. 视频标题
        # 2. 一级分类代码
        # 3. 一级分类显示名称
        videos = URLData.query.filter(
            or_(
                URLData.title.like(f'%{keyword}%'),  # 匹配标题
                URLData.fl_1.like(f'%{keyword}%'),   # 匹配分类代码
                URLData.fl_1.in_([reverse_mapping.get(cat) for cat in category_mapping.values() 
                                if keyword.lower() in cat.lower()])  # 匹配分类显示名称
            )
        ).all()
        
        # 转换结果
        video_list = []
        for video in videos:
            try:
                video_list.append({
                    'url': video.url,
                    'title': video.title,
                    'category': category_mapping.get(video.fl_1, '未知分类')
                })
            except AttributeError as e:
                print(f"视频数据缺少必要字段: {str(e)}")
                continue
                
        return jsonify({'videos': video_list})
            
    except Exception as e:
        print(f"搜索错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_category_name(fl_1):
    # 分类代码到显示名称的映射
    category_mapping = {
        'bigdata': '大数据',
        'ai': '人工智能',
        'software': '软件工程',
        'manufacturing': '智能制造',
        'repair': '家电维修',
        'service': '服务行业'
    }
    return category_mapping.get(fl_1, '未知分类')

@app.route('/static/<path:filename>')
def serve_static(filename):
    try:
        # 直接使用文件名访问static目录下的文件
        return send_from_directory(app.static_folder, filename)
    except Exception as e:
        print(f"访问文件出错: {filename}, 错误: {str(e)}")
        return str(e), 404

# 添加测试路由
@app.route('/test_videos')
def test_videos():
    """测试页面 - 直接显示static目录下的视频"""
    return """
    <html>
    <head><title>视频测试</title></head>
    <body>
        <h1>视频测试页面</h1>
        <div style="margin: 20px;">
            <h3>测试.mp4</h3>
            <video width="400" controls>
                <source src="/static/测试.mp4" type="video/mp4">
                您的浏览器不支持 video 标签。
            </video>
        </div>
        <div style="margin: 20px;">
            <h3>测试2.mp4</h3>
            <video width="400" controls>
                <source src="/static/测试2.mp4" type="video/mp4">
                您的浏览器不支持 video 标签。
            </video>
        </div>
    </body>
    </html>
    """

@app.route('/test')
def test():
    """测试页面，用于验证视频访问"""
    videos = URLData.query.all()
    html = ['<html><body><h1>视频测试页面</h1>']
    for video in videos:
        html.append(f'''
            <div style="margin: 20px;">
                <h3>{video.title}</h3>
                <video width="400" controls>
                    <source src="/{video.url}" type="video/mp4">
                    您的浏览器不支持 video 标签。
                </video>
                <p>URL: {video.url}</p>
            </div>
        ''')
    html.append('</body></html>')
    return '\n'.join(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
