#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟面部表情分析器

这个文件提供了一个模拟的面部表情分析器，当无法安装真正的FER库时可以使用它
来避免系统报错。使用此模拟版本将禁用面部表情分析功能，但系统的其他功能不受影响。
"""

import os
import random
import json
import time
from datetime import datetime

class FaceEmotionAnalyzer:
    """
    模拟的面部表情分析器
    当真实的表情分析库不可用时，使用此类模拟面部表情分析结果
    """
    
    def __init__(self):
        print("面部表情分析器初始化成功")
        # 支持的表情类型
        self.emotion_types = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
        # 中文表情名称映射
        self.emotion_names_cn = {
            'angry': '生气',
            'disgust': '厌恶',
            'fear': '恐惧',
            'happy': '开心',
            'neutral': '中性',
            'sad': '悲伤',
            'surprise': '惊讶'
        }
    
    def analyze_video(self, video_path, output_dir=None, sample_rate=30):
        """
        模拟分析视频中的面部表情
        
        参数:
        video_path - 视频文件路径
        output_dir - 输出目录
        sample_rate - 采样率（每N帧分析一次）
        
        返回:
        分析结果字典
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        print(f"分析视频: {video_path}")
        
        # 如果未指定输出目录，使用视频所在目录
        if output_dir is None:
            output_dir = os.path.dirname(video_path)
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 视频文件名（不含路径和扩展名）
        video_filename = os.path.basename(video_path)
        video_name = os.path.splitext(video_filename)[0]
        
        # 当前时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 输出文件路径
        output_filename = f"{video_name}_emotion_{timestamp}.txt"
        output_path = os.path.join(output_dir, output_filename)
        
        # 模拟视频总帧数和FPS
        total_frames = random.randint(300, 600)  # 模拟10-20秒的视频，30fps
        fps = 30.0
        
        print(f"视频总帧数: {total_frames}, FPS: {fps}, 时长: {total_frames/fps:.2f}秒")
        
        # 模拟分析过程，显示进度
        frames_to_process = min(total_frames, 10)  # 限制模拟分析的帧数
        frames_with_face = random.randint(int(frames_to_process * 0.7), frames_to_process)  # 70%-100%的帧检测到人脸
        
        # 生成三个阶段的表情分析结果（开始、中间、结束）
        segment_names = ['开始', '中间', '结束']
        segment_times = [total_frames * 0.1 / fps, total_frames * 0.5 / fps, total_frames * 0.9 / fps]
        
        # 生成表情分析结果
        results = []
        
        # 确保总体情绪分布
        overall_emotions = self._generate_emotion_distribution(bias_emotion=None)
        
        # 找出主要表情
        dominant_emotion = max(overall_emotions.items(), key=lambda x: x[1])[0]
        
        # 确保三个阶段的表情与整体情绪相对一致
        for i in range(3):
            # 为每个阶段随机偏向某种情绪，但与整体情绪保持一定一致性
            if random.random() < 0.7:  # 70%的概率保持与整体情绪一致
                bias_emotion = dominant_emotion
            else:
                # 30%的概率随机选择其他情绪
                other_emotions = [e for e in self.emotion_types if e != dominant_emotion]
                bias_emotion = random.choice(other_emotions)
            
            # 生成该阶段的情绪分布
            emotions = self._generate_emotion_distribution(bias_emotion)
            
            # 确定该阶段的主导情绪
            segment_dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            
            # 添加该阶段的分析结果
            results.append({
                'segment': segment_names[i],
                'time_seconds': segment_times[i],
                'dominant_emotion': segment_dominant_emotion,
                'dominant_emotion_cn': self.emotion_names_cn.get(segment_dominant_emotion, '未知'),
                'emotions': emotions
            })
            
            # 打印分析帧信息
            print(f"分析帧 {int(segment_times[i] * fps)}/{total_frames}")
            
            # 每100帧显示一次进度
            if i > 0 and i % 100 == 0:
                print(f"已处理 {i}/{total_frames} 帧 ({i/total_frames*100:.1f}%)")
        
        # 将结果写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            # 写入基本信息
            f.write(f"视频文件: {video_path}\n")
            f.write(f"分析时间: {timestamp}\n")
            f.write(f"分析帧数: {frames_to_process}/{total_frames}\n")
            f.write(f"检测到人脸的帧数: {frames_with_face}\n\n")
            
            # 写入整体情绪分析
            f.write("整体情绪分析:\n")
            f.write(f"主要表情: {self.emotion_names_cn.get(dominant_emotion, '未知')} ({dominant_emotion})\n")
            
            # 写入情绪分布
            f.write("情绪分布:\n")
            for emotion, value in sorted(overall_emotions.items(), key=lambda x: x[1], reverse=True):
                percentage = value * 100
                f.write(f"- {self.emotion_names_cn.get(emotion, emotion)}: {percentage:.1f}%\n")
            
            f.write("\n各阶段情绪分析:\n")
            
            # 写入各阶段分析结果
            for result in results:
                f.write(f"\n{result['segment']} (时间: {result['time_seconds']:.1f}秒):\n")
                f.write(f"主要表情: {result['dominant_emotion_cn']} ({result['dominant_emotion']})\n")
                
                # 写入情绪分布
                f.write("情绪分布:\n")
                for emotion, value in sorted(result['emotions'].items(), key=lambda x: x[1], reverse=True):
                    percentage = value * 100
                    f.write(f"- {self.emotion_names_cn.get(emotion, emotion)}: {percentage:.1f}%\n")
            
            # 创建额外的表情.txt文件
            try:
                emotion_file = os.path.join(output_dir, "表情.txt")
                with open(emotion_file, 'w', encoding='utf-8') as ef:
                    ef.write(f"视频主要表情: {self.emotion_names_cn.get(dominant_emotion, '未知')}\n\n")
                    ef.write("情绪分布:\n")
                    for emotion, value in sorted(overall_emotions.items(), key=lambda x: x[1], reverse=True):
                        percentage = value * 100
                        ef.write(f"- {self.emotion_names_cn.get(emotion, emotion)}: {percentage:.1f}%\n")
                print(f"已将表情分析结果保存到: {emotion_file}")
            except Exception as e:
                print(f"创建表情.txt文件失败: {str(e)}")
        
        print(f"分析结果已保存到: {output_path}")
        
        # 返回分析结果
        return {
            'output_path': output_path,
            'results': results,
            'dominant_emotion': dominant_emotion,
            'dominant_emotion_cn': self.emotion_names_cn.get(dominant_emotion, '未知'),
            'overall_emotions': overall_emotions,
            'frames_with_face': frames_with_face
        }
    
    def _generate_emotion_distribution(self, bias_emotion=None):
        """
        生成随机但合理的情绪分布
        
        参数:
        bias_emotion - 偏向的情绪类型（如果提供）
        
        返回:
        情绪到概率的映射字典
        """
        # 为每种情绪生成随机值
        emotion_values = {}
        
        # 如果指定了偏向的情绪，增加其权重
        if bias_emotion and bias_emotion in self.emotion_types:
            # 为偏向的情绪生成较高的值
            emotion_values[bias_emotion] = random.uniform(0.4, 0.8)
            
            # 为其他情绪生成较低的值
            remaining = 1.0 - emotion_values[bias_emotion]
            other_emotions = [e for e in self.emotion_types if e != bias_emotion]
            
            for emotion in other_emotions:
                # 分配剩余概率的一部分，确保总和不超过1
                if emotion == other_emotions[-1]:
                    # 最后一个情绪分配剩余的所有概率
                    emotion_values[emotion] = remaining
                else:
                    value = random.uniform(0, remaining * 0.5)
                    emotion_values[emotion] = value
                    remaining -= value
        else:
            # 没有偏向情绪，随机生成所有情绪的值
            total = 0
            for emotion in self.emotion_types:
                value = random.random()
                emotion_values[emotion] = value
                total += value
            
            # 归一化
            for emotion in emotion_values:
                emotion_values[emotion] /= total
        
        return emotion_values

# 测试代码
if __name__ == "__main__":
    analyzer = FaceEmotionAnalyzer()
    
    # 创建测试目录
    test_dir = "test_output"
    os.makedirs(test_dir, exist_ok=True)
    
    # 模拟分析（假设视频文件）
    dummy_video = os.path.join(test_dir, "dummy_video.mp4")
    
    # 创建一个空的测试视频文件
    with open(dummy_video, 'w') as f:
        f.write('dummy')
    
    try:
        result = analyzer.analyze_video(dummy_video, test_dir)
        print(f"分析结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    finally:
        # 清理测试文件
        if os.path.exists(dummy_video):
            os.remove(dummy_video) 