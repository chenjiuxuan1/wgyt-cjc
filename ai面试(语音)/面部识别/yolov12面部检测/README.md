# 视频情绪识别系统

这个系统基于FER（Facial Emotion Recognition）库实现了视频中的面部表情识别功能。系统分析视频中的面部表情，自动选取视频总帧数三等分位置的3帧进行情绪分析，并将结果保存为JSON和CSV格式。

## 功能特点

- 支持视频面部表情识别
- 自动选择视频1/3、2/3和结束位置的3个关键帧进行分析
- 提供JSON和CSV格式的结果输出
- 提供Flask Web界面和简单命令行工具
- 可视化显示情绪识别结果

## 安装依赖

请确保已安装Python 3.6或更高版本，然后安装所需依赖：

```bash
pip install fer opencv-python flask pandas matplotlib tqdm werkzeug moviepy
```

## 使用方法

### 1. Flask Web应用

运行Flask应用程序，提供Web界面上传视频并分析：

```bash
python 1111.py
```

或者

```bash
python fer_flask_app.py
```

然后在浏览器中访问 http://127.0.0.1:5000 即可使用Web界面。

### 2. 简单命令行工具

使用命令行工具直接分析视频：

```bash
python simple_emotion_test.py 视频路径 [--output 输出目录]
```

例如：

```bash
python simple_emotion_test.py test_video.mp4 --output results
```

## 输出结果

分析结果将保存在以下格式：

1. JSON文件：包含完整的分析信息，包括视频信息、所选帧位置和每个采样帧的情绪数据
2. CSV文件：提供情绪数据的表格形式，方便进一步分析

## 情绪类别

系统能够识别以下7种情绪：

- angry (生气)
- disgust (厌恶)
- fear (恐惧)
- happy (开心)
- sad (悲伤)
- surprise (惊讶)
- neutral (中性)

## 注意事项

- 处理大视频文件可能需要较长时间
- 建议在具有足够计算资源的环境中运行
- 系统只处理每个视频中三个等分位置的帧，可以快速获得视频整体情绪变化趋势

## 项目结构

- `1111.py` / `fer_flask_app.py`: Flask Web应用程序
- `simple_emotion_test.py`: 命令行工具
- `results/`: 存放分析结果的目录
- `uploads/`: Web上传的视频临时存储目录 