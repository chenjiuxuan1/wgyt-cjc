#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面部表情识别测试脚本

使用方法:
python test_face_emotion.py [视频文件路径]
"""

import os
import sys
from face_emotion_analyzer import FaceEmotionAnalyzer

def main():
    # 检查参数
    if len(sys.argv) < 2:
        print("用法: python test_face_emotion.py [视频文件路径]")
        return
    
    video_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.isfile(video_path):
        print(f"错误: 文件 '{video_path}' 不存在")
        return
    
    print(f"开始分析视频: {video_path}")
    
    # 创建分析器
    try:
        analyzer = FaceEmotionAnalyzer()
        # 分析视频
        result = analyzer.analyze_video(video_path)
        print("\n分析完成!")
        print(f"结果保存在: {result['output_path']}")
        
        # 显示分析结果摘要
        print("\n分析结果摘要:")
        print(f"视频总帧数: {result['total_frames']}")
        print(f"视频时长: {result['duration']:.2f}秒")
        
        # 显示每个分析点的情绪
        for i, frame_result in enumerate(result['results']):
            print(f"\n{frame_result['segment']}:")
            if frame_result['has_face']:
                print(f"  主要表情: {frame_result['dominant_emotion']}")
                # 打印前三个主要情绪
                sorted_emotions = sorted(
                    frame_result['emotions'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                for j, (emotion, score) in enumerate(sorted_emotions[:3]):
                    emotion_cn = {
                        'angry': '生气', 'disgust': '厌恶', 'fear': '恐惧',
                        'happy': '开心', 'neutral': '中性', 'sad': '悲伤',
                        'surprise': '惊讶'
                    }.get(emotion, emotion)
                    print(f"  {emotion_cn}: {score:.4f}")
            else:
                print("  未检测到面部")
    
    except Exception as e:
        print(f"分析失败: {str(e)}")

if __name__ == "__main__":
    main() 