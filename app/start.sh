#!/bin/bash

echo "========================================"
echo "Chemistry Agent API 启动脚本"
echo "========================================"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -f "run_server.py" ]; then
    echo "❌ 错误: 请在app目录下运行此脚本"
    exit 1
fi

echo "✅ 环境检查通过"
echo "🚀 启动Chemistry Agent API服务..."
echo

# 启动服务
python3 run_server.py

echo
echo "🛑 服务已停止" 