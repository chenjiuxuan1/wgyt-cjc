#!/bin/bash
echo "=========================================="
echo "AI面试系统启动脚本"
echo "=========================================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python，请先安装Python 3.8或更高版本"
    exit 1
fi

echo "检查并安装必要的依赖..."
python3 -m pip install -q flask python-dotenv moviepy

# 尝试安装面部表情分析相关依赖（可能会失败，但不影响基本功能）
echo "尝试安装面部表情分析相关依赖（可选）..."
python3 -m pip install -q fer opencv-python tensorflow &> /dev/null || true

echo "创建上传目录..."
mkdir -p uploads/sessions

echo "启动AI面试系统..."
echo "应用将在http://127.0.0.1:5000运行"
echo "可以在浏览器中访问该地址"
echo "按Ctrl+C可以停止服务器"

# 设置可执行权限
chmod +x app.py

# 启动应用
python3 app.py 