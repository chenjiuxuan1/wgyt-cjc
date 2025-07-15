#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import argparse
from datetime import datetime
from pathlib import Path
import pandas as pd

import cv2
from fer import FER
from fer.classes import Video

def analyze_video(video_path, output_dir='results'):
    """
    分析视频中的面部表情，读取视频总帧数三等分位置的3帧
    
    参数:
        video_path: 视频文件路径
        output_dir: 结果输出目录
    
    返回:
        情绪分析结果字典
    """
    print(f"开始分析视频: {video_path}")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 初始化FER检测器
    detector = FER()
    
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"无法打开视频文件: {video_path}")
        
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0
    
    # 计算三等分位置的帧号
    frame_positions = [
        int(total_frames / 3),      # 1/3位置
        int(2 * total_frames / 3),  # 2/3位置
        total_frames - 1            # 最后一帧（减1是因为帧计数从0开始）
    ]
    
    print(f"视频信息: {total_frames} 帧, {fps:.2f} fps, 时长 {duration:.2f} 秒")
    print(f"选取帧位置: {frame_positions}")
    
    # 手动处理每个位置的帧
    results = []
    
    for position in frame_positions:
        # 设置帧位置
        cap.set(cv2.CAP_PROP_POS_FRAMES, position)
        ret, frame = cap.read()
        
        if ret:
            # 检测当前帧的情绪
            faces = detector.detect_emotions(frame)
            
            if faces:
                # 只处理第一个检测到的脸
                face = faces[0]
                emotions = face['emotions']
                time_seconds = position / fps if fps > 0 else 0
                
                # 添加到结果中
                results.append({
                    'frame_number': position,
                    'time': f"{int(time_seconds // 60):02d}:{int(time_seconds % 60):02d}",
                    'time_seconds': time_seconds,
                    'emotions': emotions
                })
    
    cap.release()
    
    # 打印分析出的结果
    print("\n情绪分析结果:")
    for i, result in enumerate(results):
        print(f"帧 {result['frame_number']} (时间: {result['time']}):")
        for emotion, score in result['emotions'].items():
            print(f"  {emotion}: {score:.4f}")
        print()
    
    # 保存结果文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{Path(video_path).stem}_{timestamp}"
    
    # 创建情绪数据的DataFrame
    emotions_data = []
    for result in results:
        entry = {
            'frame_number': result['frame_number'],
            'time_seconds': result['time_seconds'],
            'time': result['time']
        }
        entry.update(result['emotions'])
        emotions_data.append(entry)
        
    emotions_df = pd.DataFrame(emotions_data)
    
    # 保存为JSON文件
    json_path = os.path.join(output_dir, f"{filename}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'video_info': {
                'total_frames': total_frames,
                'fps': fps,
                'duration_seconds': duration
            },
            'frame_positions': frame_positions,
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"JSON结果已保存至: {json_path}")
    
    # 保存为CSV格式
    if not emotions_df.empty:
        csv_path = os.path.join(output_dir, f"{filename}.csv")
        emotions_df.to_csv(csv_path, index=False)
        print(f"CSV结果已保存至: {csv_path}")
    
    return {
        'total_frames': total_frames,
        'analyzed_frames': len(results),
        'results': results,
        'json_path': json_path
    }

def main():
    parser = argparse.ArgumentParser(description='视频情绪识别工具')
    parser.add_argument('video_path', help='待分析的视频文件路径')
    parser.add_argument('--output', default='results', help='结果输出目录（默认：results）')
    
    args = parser.parse_args()
    
    try:
        analyze_video(args.video_path, args.output)
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == '__main__':
    main() 