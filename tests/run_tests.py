#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Chemistry Agent 测试运行脚本
"""

import os
import sys
import subprocess
from pathlib import Path

# 设置代理
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["https_proxy"] = "http://127.0.0.1:7897"

def run_tests():
    """运行所有测试"""
    print("🧪 Chemistry Agent 测试套件")
    print("=" * 50)
    
    # 获取当前目录
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    
    # 切换到项目根目录
    os.chdir(project_root)
    
    # 测试文件列表
    test_files = [
        "tests/test_agent.py",
        "tests/test_converters.py", 
        "tests/test_rdkit.py",
        "tests/test_safety_tools.py",
        "tests/test_search.py",
        "tests/test_api.py"
    ]
    
    print("📋 可用的测试:")
    for i, test_file in enumerate(test_files, 1):
        print(f"{i}. {test_file}")
    print("7. 运行所有测试")
    print("8. 退出")
    
    while True:
        choice = input("\n请选择要运行的测试 (1-8): ").strip()
        
        if choice == "7":
            print("\n🚀 运行所有测试...")
            try:
                # 运行所有测试
                result = subprocess.run([
                    sys.executable, "-m", "pytest", 
                    "tests/", 
                    "-v", 
                    "--tb=short"
                ], capture_output=True, text=True)
                
                print("📊 测试结果:")
                print(result.stdout)
                if result.stderr:
                    print("❌ 错误信息:")
                    print(result.stderr)
                    
            except Exception as e:
                print(f"❌ 运行测试失败: {e}")
                
        elif choice == "8":
            print("👋 再见!")
            break
            
        elif choice.isdigit() and 1 <= int(choice) <= 6:
            test_file = test_files[int(choice) - 1]
            print(f"\n🧪 运行测试: {test_file}")
            
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest", 
                    test_file, 
                    "-v", 
                    "--tb=short"
                ], capture_output=True, text=True)
                
                print("📊 测试结果:")
                print(result.stdout)
                if result.stderr:
                    print("❌ 错误信息:")
                    print(result.stderr)
                    
            except Exception as e:
                print(f"❌ 运行测试失败: {e}")
        else:
            print("❌ 无效选择，请重新输入")

def check_dependencies():
    """检查测试依赖"""
    print("🔍 检查测试依赖...")
    
    required_packages = [
        "pytest",
        "requests",
        "rdkit",
        "langchain",
        "fastapi",
        "uvicorn"
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

def main():
    """主函数"""
    print("🧪 Chemistry Agent 测试运行器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 运行测试
    run_tests()

if __name__ == "__main__":
    main() 