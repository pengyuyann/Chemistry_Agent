@echo off
chcp 65001 >nul
echo ========================================
echo Chemistry Agent API 启动脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查是否在正确的目录
if not exist "run_server.py" (
    echo ❌ 错误: 请在app目录下运行此脚本
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo 🚀 启动Chemistry Agent API服务...
echo.

REM 启动服务
python run_server.py

echo.
echo 🛑 服务已停止
pause 