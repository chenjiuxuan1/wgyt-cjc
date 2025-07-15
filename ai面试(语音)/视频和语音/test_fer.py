#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试FER库是否可用
"""

import sys
import importlib

def check_module(module_name):
    """检查模块是否已安装并打印详细信息"""
    print(f"正在检查模块: {module_name}")
    try:
        module = importlib.import_module(module_name)
        print(f"✅ 模块 '{module_name}' 已成功导入")
        
        # 打印版本号（如果可用）
        if hasattr(module, '__version__'):
            print(f"   版本: {module.__version__}")
        elif hasattr(module, 'version'):
            print(f"   版本: {module.version}")
        
        # 打印模块路径
        print(f"   路径: {module.__file__}")
        
        return True
    except ImportError as e:
        print(f"❌ 导入模块 '{module_name}' 失败: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 检查模块 '{module_name}' 时出错: {str(e)}")
        return False

def main():
    """主函数"""
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"模块搜索路径:")
    for i, path in enumerate(sys.path):
        print(f"  {i+1}. {path}")
    
    print("\n" + "="*60 + "\n")
    
    # 检查必要的依赖
    dependencies = ["numpy", "cv2", "fer"]
    all_available = True
    
    for module in dependencies:
        if not check_module(module):
            all_available = False
        print("")
    
    # 如果FER可用，尝试创建检测器
    if all_available:
        try:
            from fer import FER
            detector = FER()
            print("✅ 成功创建FER检测器实例")
        except Exception as e:
            print(f"❌ 创建FER检测器实例失败: {str(e)}")
            all_available = False
    
    print("\n" + "="*60)
    if all_available:
        print("✅ 所有依赖检查通过，FER库可用")
    else:
        print("❌ 部分依赖检查失败，FER库可能不可用")

if __name__ == "__main__":
    main() 