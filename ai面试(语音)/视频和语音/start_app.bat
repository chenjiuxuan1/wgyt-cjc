@echo off
echo ===========================================
echo AI面试系统启动脚本
echo ===========================================

REM 检查Python是否安装
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

echo 检查并安装必要的依赖...
python -m pip install -q flask dotenv moviepy python-dotenv

REM 尝试安装面部表情分析相关依赖（可能会失败，但不影响基本功能）
echo 尝试安装面部表情分析相关依赖（可选）...
python -m pip install -q fer opencv-python tensorflow >nul 2>nul

echo 创建上传目录...
if not exist "uploads" mkdir uploads
if not exist "uploads\sessions" mkdir uploads\sessions

echo 启动AI面试系统...
echo 应用将在http://127.0.0.1:5000运行
echo 可以在浏览器中访问该地址
echo 按Ctrl+C可以停止服务器

python app.py

pause 