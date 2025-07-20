#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
服务器诊断脚本
帮助诊断 Chemistry Agent API 服务器启动问题
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def check_env_file():
    """检查.env文件"""
    print("🔍 检查 .env 文件...")
    print("=" * 40)
    
    if os.path.exists(".env"):
        print("✅ .env 文件存在")
        
        # 加载环境变量
        load_dotenv()
        
        # 检查关键环境变量
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            masked_key = deepseek_key[:4] + "*" * (len(deepseek_key) - 8) + deepseek_key[-4:] if len(deepseek_key) > 8 else "***"
            print(f"✅ DEEPSEEK_API_KEY: {masked_key}")
        else:
            print("❌ DEEPSEEK_API_KEY 未设置")
        
        host = os.getenv("HOST", "0.0.0.0")
        port = os.getenv("PORT", "8000")
        print(f"✅ HOST: {host}")
        print(f"✅ PORT: {port}")
        
        return True
    else:
        print("❌ .env 文件不存在")
        return False

def check_dependencies():
    """检查依赖包"""
    print("\n🔍 检查依赖包...")
    print("=" * 40)
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "python-dotenv",
        "requests",
        "pydantic"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_app_structure():
    """检查应用结构"""
    print("\n🔍 检查应用结构...")
    print("=" * 40)
    
    required_files = [
        "app/api/main.py",
        "app/api/endpoints/chemagent_chat.py",
        "app/core/agents/__init__.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 不存在")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  缺少文件: {', '.join(missing_files)}")
        return False
    
    print("✅ 应用结构完整")
    return True

def test_server_start():
    """测试服务器启动"""
    print("\n🚀 测试服务器启动...")
    print("=" * 40)
    
    try:
        # 切换到app目录
        if os.path.exists("app"):
            os.chdir("app")
            print("✅ 切换到 app 目录")
        else:
            print("❌ app 目录不存在")
            return False
        
        # 尝试导入模块
        try:
            import api.main
            print("✅ 成功导入 api.main")
        except ImportError as e:
            print(f"❌ 导入 api.main 失败: {e}")
            return False
        
        # 尝试启动服务器（短暂测试）
        print("🔄 尝试启动服务器（5秒测试）...")
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "api.main:app",
            "--host", "127.0.0.1",
            "--port", "8001",  # 使用不同端口避免冲突
            "--timeout-keep-alive", "5"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待5秒
        import time
        time.sleep(5)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ 服务器启动成功")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print("❌ 服务器启动失败")
            print(f"错误输出: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 Chemistry Agent API 服务器诊断工具")
    print("=" * 50)
    
    # 检查各项
    env_ok = check_env_file()
    deps_ok = check_dependencies()
    structure_ok = check_app_structure()
    
    if env_ok and deps_ok and structure_ok:
        print("\n✅ 基础检查通过，开始测试服务器启动...")
        server_ok = test_server_start()
        
        if server_ok:
            print("\n🎉 所有检查通过！服务器可以正常启动")
            print("\n💡 启动服务器的方法:")
            print("1. python start_server.py")
            print("2. cd app && python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload")
        else:
            print("\n❌ 服务器启动失败，请检查错误信息")
    else:
        print("\n❌ 基础检查失败，请先解决上述问题")

if __name__ == "__main__":
    main() 