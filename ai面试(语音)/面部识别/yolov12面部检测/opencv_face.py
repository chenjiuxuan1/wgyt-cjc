import cv2
import os
import time
import uuid
import logging
import shutil
import numpy as np
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
from fer import FER
from datetime import timedelta
import threading
from werkzeug.utils import secure_filename

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = r'E:\yolov12面部检测\final'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'wmv'}

# 确保上传和结果目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# 存储正在处理的任务
tasks = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def format_time_for_filename(td):
    """将timedelta格式化为适合文件名的字符串"""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours}h{minutes}m{seconds}s"

def process_video(video_path, output_dir, interval, task_id):
    """处理视频并检测表情"""
    try:
        logger.info(f"开始处理任务 {task_id}, 视频: {video_path}, 输出目录: {output_dir}")
        
        # 创建示例图像确保目录权限正常
        test_file = os.path.join(output_dir, "test.txt")
        try:
            with open(test_file, 'w') as f:
                f.write("测试文件权限")
            logger.info(f"成功写入测试文件: {test_file}")
            os.remove(test_file)
        except Exception as e:
            logger.error(f"无法写入测试文件，可能是权限问题: {str(e)}")
            tasks[task_id]['status'] = '失败'
            tasks[task_id]['message'] = f"错误: 无法写入到输出目录 {output_dir}, 原因: {str(e)}"
            return
        
        # 初始化FER检测器
        detector = FER()
        
        # 打开视频文件
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"无法打开视频文件: {video_path}")
            tasks[task_id]['status'] = '失败'
            tasks[task_id]['message'] = f"错误: 无法打开视频文件 {video_path}"
            return
        
        # 获取视频信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        logger.info(f"视频信息: FPS={fps}, 总帧数={total_frames}, 时长={duration}秒")
        
        # 更新任务信息
        tasks[task_id]['total_frames'] = total_frames
        tasks[task_id]['duration'] = str(timedelta(seconds=duration))
        tasks[task_id]['fps'] = fps
        
        # 每interval秒的帧数
        frames_per_interval = int(fps * interval)
        frame_count = 0
        saved_count = 0
        
        # 如果没有找到人脸，强制每500帧保存一次图像
        frames_without_face = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            frames_without_face += 1
            
            # 更新进度
            tasks[task_id]['current_frame'] = frame_count
            tasks[task_id]['progress'] = int((frame_count / total_frames) * 100)
            
            # 每interval秒检测一次表情，或如果长时间没有人脸则强制保存
            if frame_count % frames_per_interval == 0 or frame_count == 1 or frames_without_face >= 500:
                current_time = frame_count / fps
                time_str = format_time_for_filename(timedelta(seconds=current_time))
                
                # 检测表情
                results = detector.detect_emotions(frame)
                
                # 在图像上标记结果
                found_face = False
                for face in results:
                    found_face = True
                    frames_without_face = 0
                    (x, y, w, h) = face["box"]
                    emotion, score = max(face["emotions"].items(), key=lambda x: x[1])
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cv2.putText(frame, f"{emotion}: {score:.2f}", (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                
                # 如果没有人脸，添加文本说明
                if not found_face and frames_without_face >= 500:
                    cv2.putText(frame, "未检测到人脸", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # 无论有没有人脸都保存图像（至少保存一些参考帧）
                output_path = os.path.join(output_dir, f"emotion_{saved_count:03d}_{time_str}.jpg")
                
                try:
                    success = cv2.imwrite(output_path, frame)
                    if not success:
                        logger.error(f"保存图像失败: {output_path}")
                    else:
                        logger.info(f"成功保存图像: {output_path}")
                        # 相对路径，用于在网页中显示
                        rel_path = os.path.relpath(output_path, app.config['RESULTS_FOLDER'])
                        tasks[task_id]['results'].append(rel_path)
                        saved_count += 1
                        
                        # 直接复制一份到final根目录便于查看
                        root_copy = os.path.join(app.config['RESULTS_FOLDER'], f"latest_{task_id}.jpg")
                        shutil.copy2(output_path, root_copy)
                except Exception as e:
                    logger.error(f"保存图像时出错: {str(e)}")
        
        cap.release()
        
        # 检查是否有任何结果
        if saved_count == 0:
            logger.warning(f"任务 {task_id} 没有保存任何结果")
            # 创建一个空白图像，表明处理完成但没有人脸
            blank_img = 255 * np.ones(shape=[300, 500, 3], dtype=np.uint8)
            cv2.putText(blank_img, "处理完成，未检测到人脸", (30, 150), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            blank_path = os.path.join(output_dir, "no_faces_found.jpg")
            cv2.imwrite(blank_path, blank_img)
            tasks[task_id]['results'].append(os.path.relpath(blank_path, app.config['RESULTS_FOLDER']))
        
        tasks[task_id]['status'] = '完成'
        tasks[task_id]['message'] = f"检测完成，共保存了 {saved_count} 张结果图像"
        logger.info(f"任务 {task_id} 完成，保存了 {saved_count} 张图像")
    except Exception as e:
        logger.error(f"任务 {task_id} 处理过程中出错: {str(e)}")
        tasks[task_id]['status'] = '失败'
        tasks[task_id]['message'] = f"处理过程中出错: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logger.warning("没有上传文件")
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("选择的文件名为空")
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # 生成唯一任务ID
        task_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}_{filename}")
        
        try:
            file.save(video_path)
            logger.info(f"上传的视频保存到: {video_path}")
        except Exception as e:
            logger.error(f"保存上传文件时出错: {str(e)}")
            return "文件上传失败，请检查权限或磁盘空间", 500
        
        # 设置检测间隔（秒）
        try:
            interval = float(request.form.get('interval', 10))
        except ValueError:
            interval = 10
        
        # 创建输出目录
        output_dir = os.path.join(app.config['RESULTS_FOLDER'], task_id)
        try:
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"创建输出目录: {output_dir}")
        except Exception as e:
            logger.error(f"创建输出目录时出错: {str(e)}")
            return "无法创建输出目录，请检查权限", 500
        
        # 创建任务记录
        tasks[task_id] = {
            'video_name': filename,
            'status': '处理中',
            'interval': interval,
            'start_time': time.time(),
            'output_dir': output_dir,
            'results': [],
            'progress': 0,
            'current_frame': 0,
            'total_frames': 0
        }
        
        # 在后台线程处理视频
        thread = threading.Thread(target=process_video, args=(video_path, output_dir, interval, task_id))
        thread.daemon = True
        thread.start()
        
        logger.info(f"启动任务 {task_id} 处理线程")
        return redirect(url_for('view_task', task_id=task_id))
    
    logger.warning(f"不支持的文件类型: {file.filename}")
    return redirect(url_for('index'))

@app.route('/task/<task_id>')
def view_task(task_id):
    if task_id not in tasks:
        logger.warning(f"请求的任务不存在: {task_id}")
        return redirect(url_for('index'))
    
    return render_template('task.html', task=tasks[task_id], task_id=task_id)

@app.route('/task_status/<task_id>')
def task_status(task_id):
    if task_id not in tasks:
        logger.warning(f"请求状态的任务不存在: {task_id}")
        return jsonify({'error': '任务不存在'})
    
    return jsonify(tasks[task_id])

@app.route('/results/<path:filename>')
def download_file(filename):
    # 构建文件的绝对路径
    file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    directory = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    
    logger.info(f"请求下载文件: {file_path}")
    if not os.path.exists(file_path):
        logger.warning(f"请求的文件不存在: {file_path}")
    
    return send_from_directory(directory, file_name)

if __name__ == "__main__":
    logger.info("应用程序启动")
    app.run(debug=True, host='0.0.0.0')