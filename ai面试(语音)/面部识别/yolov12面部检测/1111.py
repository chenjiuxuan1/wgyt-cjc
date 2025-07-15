#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
from pathlib import Path
import pandas as pd

import cv2
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from fer import FER
from fer.classes import Video

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv'}

# 确保上传和结果目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

class EmotionVideoAnalyzer:
    def __init__(self, video_path):
        self.video_path = video_path
        self.detector = FER()
        
    def analyze_video(self):
        # 创建视频对象
        video = Video(self.video_path, outdir="output")
        
        # 打开视频文件
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise Exception("无法打开视频文件")
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # 计算三等分位置的帧号
        frame_positions = [
            int(total_frames / 3),      # 1/3位置
            int(2 * total_frames / 3),  # 2/3位置
            total_frames - 1            # 最后一帧（减1是因为帧计数从0开始）
        ]
        
        print(f"视频总帧数: {total_frames}, 选取帧位置: {frame_positions}")
        
        # 手动处理每个位置的帧
        results = []
        
        for position in frame_positions:
            # 设置帧位置
            cap.set(cv2.CAP_PROP_POS_FRAMES, position)
            ret, frame = cap.read()
            
            if ret:
                # 检测当前帧的情绪
                faces = self.detector.detect_emotions(frame)
                
                if faces:
                    # 只处理第一个检测到的脸
                    face = faces[0]
                    emotions = face['emotions']
                    
                    # 添加到结果中
                    results.append({
                        'frame_number': position,
                        'time_seconds': position / fps if fps > 0 else 0,
                        'emotions': emotions
                    })
        
        cap.release()
        
        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{Path(self.video_path).stem}_{timestamp}"
        
        # 保存为JSON文件
        json_path = os.path.join(app.config['RESULTS_FOLDER'], f"{filename}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 创建情绪数据的DataFrame
        emotions_data = []
        for result in results:
            entry = {'frame_number': result['frame_number']}
            entry.update(result['emotions'])
            emotions_data.append(entry)
            
        emotions_df = pd.DataFrame(emotions_data)
        
        # 保存为CSV格式
        if not emotions_df.empty:
            csv_path = os.path.join(app.config['RESULTS_FOLDER'], f"{filename}.csv")
            emotions_df.to_csv(csv_path, index=False)
            
        return {
            'total_frames': total_frames,
            'analyzed_frames': len(results),
            'results': results,
            'json_path': json_path
        }

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>表情识别系统</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                color: #333;
                text-align: center;
            }
            form {
                background-color: #f5f5f5;
                padding: 20px;
                border-radius: 5px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            .btn {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            .btn:hover {
                background-color: #45a049;
            }
            #results {
                margin-top: 20px;
                display: none;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <h1>视频表情识别系统</h1>
        <form id="upload-form" enctype="multipart/form-data">
            <div class="form-group">
                <label for="video">选择视频文件:</label>
                <input type="file" id="video" name="video" accept=".mp4,.avi,.mov,.mkv">
            </div>
            <button type="submit" class="btn">上传并分析</button>
        </form>
        
        <div id="loading" style="display:none; text-align:center; margin-top:20px;">
            <p>视频分析中，请稍候...</p>
        </div>
        
        <div id="results">
            <h2>分析结果</h2>
            <div id="result-summary"></div>
            <h3>3帧情绪数据</h3>
            <table id="emotions-table">
                <thead>
                    <tr>
                        <th>帧号</th>
                        <th>时间点(秒)</th>
                        <th>生气</th>
                        <th>厌恶</th>
                        <th>恐惧</th>
                        <th>开心</th>
                        <th>中性</th>
                        <th>悲伤</th>
                        <th>惊讶</th>
                    </tr>
                </thead>
                <tbody id="emotions-data">
                </tbody>
            </table>
            <div id="download-links" style="margin-top:20px;"></div>
        </div>
        
        <script>
            document.getElementById('upload-form').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData();
                const videoFile = document.getElementById('video').files[0];
                
                if (!videoFile) {
                    alert('请选择视频文件');
                    return;
                }
                
                formData.append('video', videoFile);
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('results').style.display = 'none';
                
                fetch('/analyze', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('results').style.display = 'block';
                    
                    document.getElementById('result-summary').innerHTML = 
                        `<p>视频总帧数: ${data.total_frames}<br>分析帧数: ${data.analyzed_frames}</p>`;
                    
                    const tbody = document.getElementById('emotions-data');
                    tbody.innerHTML = '';
                    
                    data.results.forEach(item => {
                        const row = document.createElement('tr');
                        
                        row.innerHTML = `
                            <td>${item.frame_number}</td>
                            <td>${item.time_seconds.toFixed(2)}</td>
                            <td>${item.emotions.angry ? item.emotions.angry.toFixed(4) : 0}</td>
                            <td>${item.emotions.disgust ? item.emotions.disgust.toFixed(4) : 0}</td>
                            <td>${item.emotions.fear ? item.emotions.fear.toFixed(4) : 0}</td>
                            <td>${item.emotions.happy ? item.emotions.happy.toFixed(4) : 0}</td>
                            <td>${item.emotions.neutral ? item.emotions.neutral.toFixed(4) : 0}</td>
                            <td>${item.emotions.sad ? item.emotions.sad.toFixed(4) : 0}</td>
                            <td>${item.emotions.surprise ? item.emotions.surprise.toFixed(4) : 0}</td>
                        `;
                        
                        tbody.appendChild(row);
                    });
                    
                    const downloadLinks = document.getElementById('download-links');
                    downloadLinks.innerHTML = `
                        <p><a href="/download/${data.json_filename}" download>下载JSON结果</a></p>
                        <p><a href="/download/${data.csv_filename}" download>下载CSV结果</a></p>
                    `;
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('loading').style.display = 'none';
                    alert('分析视频时出错，请查看控制台获取详细信息');
                });
            });
        </script>
    </body>
    </html>
    '''

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'video' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
        
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            analyzer = EmotionVideoAnalyzer(file_path)
            result = analyzer.analyze_video()
            
            # 提取JSON和CSV文件名
            json_filename = os.path.basename(result['json_path'])
            csv_filename = json_filename.replace('.json', '.csv')
            
            # 返回处理结果
            return jsonify({
                'total_frames': result['total_frames'],
                'analyzed_frames': result['analyzed_frames'],
                'results': result['results'],
                'json_filename': json_filename,
                'csv_filename': csv_filename
            })
            
        except Exception as e:
            return jsonify({'error': f'视频分析失败: {str(e)}'}), 500
    
    return jsonify({'error': '不支持的文件类型'}), 400

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['RESULTS_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True) 