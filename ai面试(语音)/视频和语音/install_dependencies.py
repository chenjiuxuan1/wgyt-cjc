#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面部表情识别功能依赖安装脚本

此脚本用于安装面部表情识别功能所需的全部依赖，
包括fer库、opencv-python和numpy。
"""

import os
import sys
import subprocess
import time

def print_section(title):
    """打印带分隔符的标题"""
    width = 60
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width + "\n")

def check_module(module_name):
    """检查模块是否已安装"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """安装指定的包"""
    print(f"正在安装 {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} 安装成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package_name} 安装失败: {str(e)}")
        return False

def main():
    """主函数"""
    print_section("面部表情识别功能依赖安装")
    
    print("此脚本将安装面部表情识别功能所需的依赖")
    print("包括: fer, opencv-python, numpy")
    print("\n注意: 安装过程可能需要几分钟时间，请耐心等待")
    
    # 检查Python版本
    print(f"\nPython版本: {sys.version}")
    
    # 确认是否继续
    try:
        answer = input("\n是否继续安装? (y/n): ").strip().lower()
        if answer != 'y':
            print("安装已取消")
            return
    except (KeyboardInterrupt, EOFError):
        print("\n安装已取消")
        return
    
    print_section("开始安装")
    
    # 安装必要的依赖
    dependencies = ["numpy", "opencv-python", "fer"]
    success = True
    
    for package in dependencies:
        if check_module(package.split('-')[0]):
            print(f"✅ {package} 已安装")
        else:
            if not install_package(package):
                success = False
    
    print_section("安装结果")
    
    if success:
        print("✅ 所有依赖安装成功!")
        print("\n您现在可以使用面部表情识别功能了")
        print("请重新启动应用程序以应用更改")
    else:
        print("❌ 部分依赖安装失败")
        print("\n可能的解决方案:")
        print("1. 确保网络连接正常")
        print("2. 尝试手动安装失败的依赖:")
        print("   pip install numpy opencv-python fer")
        print("3. 如果继续失败，可以使用模拟面部表情分析器:")
        print("   python -c \"import shutil; shutil.copy('视频和语音/mock_face_emotion_analyzer.py', '视频和语音/face_emotion_analyzer.py')\"")
    
    print("\n按回车键退出...")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass

if __name__ == "__main__":
    main() 