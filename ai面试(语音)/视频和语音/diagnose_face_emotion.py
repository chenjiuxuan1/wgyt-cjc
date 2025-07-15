#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面部表情分析功能诊断脚本

此脚本用于检查面部表情分析功能所需的依赖是否正确安装，
并提供详细的问题排查指南。
"""

import os
import sys
import importlib
import subprocess

def print_section(title):
    """打印带分隔符的标题"""
    width = 60
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width + "\n")

def check_file_exists(filename, directory='.'):
    """检查文件是否存在"""
    filepath = os.path.join(directory, filename)
    exists = os.path.isfile(filepath)
    status = "✅ 存在" if exists else "❌ 不存在"
    print(f"文件 '{filename}': {status}")
    if exists:
        print(f"  完整路径: {os.path.abspath(filepath)}")
    return exists, filepath

def check_module_installed(module_name):
    """检查模块是否已安装"""
    try:
        importlib.import_module(module_name)
        print(f"模块 '{module_name}': ✅ 已安装")
        return True
    except ImportError:
        print(f"模块 '{module_name}': ❌ 未安装")
        return False

def try_install_module(module_name):
    """尝试安装模块"""
    print(f"正在尝试安装 {module_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
        print(f"✅ {module_name} 安装成功!")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ {module_name} 安装失败")
        return False

def check_face_emotion_analyzer():
    """检查面部表情分析器的可用性"""
    try:
        # 尝试导入
        from face_emotion_analyzer import FaceEmotionAnalyzer
        analyzer = FaceEmotionAnalyzer()
        print("✅ 面部表情分析器可用")
        return True
    except ImportError as e:
        print(f"❌ 导入面部表情分析器时出错: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 初始化面部表情分析器时出错: {str(e)}")
        return False

def main():
    """主函数"""
    print_section("面部表情分析功能诊断")
    
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python版本: {sys.version}")
    
    print_section("检查文件")
    app_exists, app_path = check_file_exists("app.py", "视频和语音")
    analyzer_exists, analyzer_path = check_file_exists("face_emotion_analyzer.py", "视频和语音")
    
    if not analyzer_exists:
        print("\n❌ 未找到面部表情分析器文件，这是导致功能不可用的主要原因")
        print("  请确保face_emotion_analyzer.py文件位于视频和语音目录下")
    
    print_section("检查依赖")
    fer_installed = check_module_installed("fer")
    cv2_installed = check_module_installed("cv2")
    numpy_installed = check_module_installed("numpy")
    
    if not fer_installed or not cv2_installed or not numpy_installed:
        print("\n❌ 缺少必要的依赖，这会导致面部表情识别功能不可用")
        
        answer = input("\n是否尝试自动安装缺失的依赖? (y/n): ").strip().lower()
        if answer == 'y':
            if not fer_installed:
                try_install_module("fer")
            if not cv2_installed:
                try_install_module("opencv-python")
            if not numpy_installed:
                try_install_module("numpy")
        else:
            print("跳过依赖安装")
    
    print_section("测试面部表情分析器")
    if analyzer_exists and fer_installed and cv2_installed and numpy_installed:
        # 添加父目录到sys.path，以便能够导入模块
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
            
        # 切换到视频和语音目录尝试导入
        os.chdir(os.path.dirname(analyzer_path))
        analyzer_works = check_face_emotion_analyzer()
        
        if not analyzer_works:
            print("\n❌ 面部表情分析器无法正常工作")
            print("  这可能是由于FER库的版本不兼容或其他问题导致的")
    
    print_section("总结")
    
    if not analyzer_exists:
        print("1. 面部表情分析器文件不存在")
        print("   解决方案: 重新创建face_emotion_analyzer.py文件")
        print("   确保它位于视频和语音目录下")
    
    if not (fer_installed and cv2_installed and numpy_installed):
        print("2. 缺少必要依赖")
        print("   解决方案: 运行以下命令安装依赖")
        print("   pip install fer opencv-python numpy")
        print("   或运行安装脚本:")
        print("   python 视频和语音/install_dependencies.py")
    
    if analyzer_exists and fer_installed and cv2_installed and numpy_installed and not analyzer_works:
        print("3. 面部表情分析器无法工作")
        print("   解决方案: 检查face_emotion_analyzer.py文件内容是否正确")
        print("   尝试重新创建该文件或更新FER库")
    
    if analyzer_exists and fer_installed and cv2_installed and numpy_installed and analyzer_works:
        print("✅ 所有检查都通过了")
        print("如果应用仍然提示'面部表情分析模块未找到'，")
        print("可能是由于Python路径问题导致的。")
        print("尝试在运行app.py时使用绝对路径或设置PYTHONPATH环境变量。")
    
    print("\n如需禁用面部表情分析功能并继续使用系统的其他功能，")
    print("可以修改app.py中的导入部分，或者运行:")
    print("python -c \"open('视频和语音/face_emotion_analyzer.py', 'w').write('# 空文件')\"")

if __name__ == "__main__":
    main() 