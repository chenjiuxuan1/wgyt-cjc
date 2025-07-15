#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面试系统及面部表情识别功能全部依赖安装脚本

此脚本用于安装系统所需的全部依赖：
1. 基础依赖：flask, python-dotenv, sqlite3等
2. 面部表情识别依赖：fer, opencv-python, numpy等
"""

import os
import sys
import subprocess
import platform
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
    print_section("面试系统及面部表情识别功能依赖安装")
    
    print("此脚本将安装面试系统和面部表情识别功能所需的全部依赖")
    print("包括基础依赖和面部表情识别依赖")
    print("\n注意: 安装过程可能需要几分钟时间，请耐心等待")
    
    # 检查Python版本
    print(f"\nPython版本: {sys.version}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    
    # 确认是否继续
    try:
        answer = input("\n是否继续安装? (y/n): ").strip().lower()
        if answer != 'y':
            print("安装已取消")
            return
    except (KeyboardInterrupt, EOFError):
        print("\n安装已取消")
        return
    
    print_section("安装基础依赖")
    
    # 基础依赖
    base_dependencies = [
        "flask",
        "python-dotenv",
        "numpy",
        "pandas",
        "ollama",
        "requests"
    ]
    
    base_success = True
    for package in base_dependencies:
        if check_module(package.split('-')[0]):
            print(f"✅ {package} 已安装")
        else:
            if not install_package(package):
                base_success = False
    
    print_section("安装面部表情识别依赖")
    
    # 面部表情识别依赖
    fer_dependencies = [
        "opencv-python",
        "moviepy",
        "fer"
    ]
    
    fer_success = True
    for package in fer_dependencies:
        if check_module(package.split('-')[0]):
            print(f"✅ {package} 已安装")
        else:
            if not install_package(package):
                fer_success = False
    
    print_section("安装结果")
    
    if base_success and fer_success:
        print("✅ 所有依赖安装成功!")
        print("\n您现在可以使用面试系统的所有功能，包括面部表情识别")
        print("请使用以下命令启动系统:")
        print("python 视频和语音/app.py")
    else:
        print("⚠️ 部分依赖安装失败")
        
        if not base_success:
            print("\n基础依赖未完全安装，可能会影响系统的基本功能")
            print("请手动安装缺失的依赖:")
            print("pip install flask python-dotenv numpy pandas ollama requests")
        
        if not fer_success:
            print("\n面部表情识别依赖未完全安装，可能会导致表情识别功能不可用")
            print("您仍然可以使用系统的其他功能")
            print("如果需要启用表情识别，请手动安装缺失的依赖:")
            print("pip install opencv-python moviepy fer")
            print("\n或者使用模拟面部表情分析器:")
            print("python -c \"import shutil; shutil.copy('视频和语音/mock_face_emotion_analyzer.py', '视频和语音/face_emotion_analyzer.py')\"")
    
    print("\n按回车键退出...")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass

if __name__ == "__main__":
    main() 