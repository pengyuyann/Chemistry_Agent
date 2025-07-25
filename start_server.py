'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/24 15:43
@Author  : JunYU
@File    : start_server
'''
# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Chemistry Agent API 启动脚本
"""

import os
import sys
import subprocess
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置代理
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["https_proxy"] = "http://127.0.0.1:7897"


def check_dependencies():
    """检查依赖包"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "requests",
        "pydantic",
        "python-dotenv"
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False

    print("✅ 所有依赖包已安装")
    return True


def check_environment():
    """检查环境变量"""
    required_env_vars = [
        "DEEPSEEK_API_KEY"
    ]

    missing_env_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_env_vars.append(var)

    if missing_env_vars:
        print(f"⚠️ 缺少环境变量: {', '.join(missing_env_vars)}")
        print("请按照以下步骤设置环境变量:")
        print("\n1. 复制 env_example.txt 为 .env 文件")
        print("2. 编辑 .env 文件，填入你的API密钥")
        print("3. 重新运行此脚本")
        print("\n或者使用以下命令设置环境变量:")
        print("\nWindows PowerShell:")
        for var in missing_env_vars:
            print(f"$env:{var} = 'your_api_key_here'")
        print("\nWindows CMD:")
        for var in missing_env_vars:
            print(f"set {var}=your_api_key_here")
        print("\n注意: 某些功能可能无法正常工作")
    else:
        print("✅ 环境变量检查通过")

    return True


def start_server():
    """启动API服务器"""
    print("🚀 启动 Chemistry Agent API 服务器...")

    # 切换到app目录
    os.chdir("app")

    # 启动服务器
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")


def main():
    """主函数"""
    print("🧪 Chemistry Agent API 启动器")
    print("=" * 40)

    # 检查环境
    check_environment()

    print("\n📋 启动选项:")
    print("1. 启动API服务器")
    print("2. 运行测试")
    print("3. 退出")

    while True:
        choice = input("\n请选择 (1-3): ").strip()

        if choice == "1":
            start_server()
            break
        elif choice == "2":
            print("🧪 运行测试...")
            subprocess.run([sys.executable, "test_chemagent.py"])
            break
        elif choice == "3":
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请重新输入")


if __name__ == "__main__":
    main()