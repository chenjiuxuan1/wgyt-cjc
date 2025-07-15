#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面部表情分析测试脚本

此脚本用于测试更新后的面部表情分析功能。
使用方法:
python test_video_emotion.py [视频文件路径]
"""

import os
import sys
import time
from face_emotion_analyzer import FaceEmotionAnalyzer

def print_section(title):
    """打印带分隔符的标题"""
    width = 60
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width + "\n")

def main():
    # 检查参数
    if len(sys.argv) < 2:
        print("用法: python test_video_emotion.py [视频文件路径]")
        return
    
    video_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.isfile(video_path):
        print(f"错误: 文件 '{video_path}' 不存在")
        return
    
    print_section(f"开始分析视频: {os.path.basename(video_path)}")
    
    # 创建分析器
    try:
        print("初始化面部表情分析器...")
        analyzer = FaceEmotionAnalyzer()
        
        # 设置较低的采样率以加快处理速度
        sample_rate = 10
        if len(sys.argv) > 2:
            try:
                sample_rate = int(sys.argv[2])
            except ValueError:
                pass
        
        print(f"使用采样率: 每{sample_rate}帧分析一次")
        
        # 记录开始时间
        start_time = time.time()
        
        # 分析视频
        print("正在分析视频，请稍候...")
        result = analyzer.analyze_video(video_path, sample_rate=sample_rate)
        
        # 计算处理时间
        elapsed_time = time.time() - start_time
        
        print_section("分析完成!")
        print(f"处理时间: {elapsed_time:.2f}秒")
        print(f"结果保存在: {result['output_path']}")
        
        # 显示分析结果摘要
        print_section("分析结果摘要")
        print(f"视频总帧数: {result['total_frames']}")
        print(f"视频时长: {result['duration']:.2f}秒")
        print(f"检测到人脸的帧数: {result['frames_with_face']}")
        
        # 显示整体情绪分析
        if 'dominant_emotion_cn' in result:
            print(f"\n主要表情: {result['dominant_emotion_cn']} ({result['dominant_emotion']})")
            
            # 排序显示情绪分布
            if 'overall_emotions' in result:
                print("\n整体情绪分布:")
                sorted_emotions = sorted(
                    result['overall_emotions'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                for emotion, score in sorted_emotions:
                    emotion_cn = {
                        'angry': '生气', 'disgust': '厌恶', 'fear': '恐惧',
                        'happy': '开心', 'neutral': '中性', 'sad': '悲伤',
                        'surprise': '惊讶'
                    }.get(emotion, emotion)
                    
                    # 创建简单的可视化条形图
                    bar_length = int(score * 40)
                    bar = '█' * bar_length
                    print(f"  {emotion_cn}: {score:.4f} {bar}")
        
        # 显示每个分析点的情绪
        print_section("视频各阶段分析")
        
        for i, segment_result in enumerate(result['results']):
            print(f"\n{segment_result['segment']}:")
            if segment_result['has_face']:
                print(f"  主要表情: {segment_result.get('dominant_emotion_cn', segment_result['dominant_emotion'])}")
                
                # 打印前三个主要情绪
                sorted_emotions = sorted(
                    segment_result['emotions'].items(),
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
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 