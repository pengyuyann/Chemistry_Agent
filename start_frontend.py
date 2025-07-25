#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Chemistry Agent 前端启动器
支持向量数据库管理和人类反馈管理功能
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_node_installed():
    """检查Node.js是否已安装"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js版本: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def check_npm_installed():
    """检查npm是否已安装"""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm版本: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def install_dependencies():
    """安装前端依赖"""
    print("📦 安装前端依赖...")
    try:
        result = subprocess.run(['npm', 'install'], cwd='frontend', check=True)
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def start_frontend():
    """启动前端开发服务器"""
    print("🚀 启动前端开发服务器...")
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['REACT_APP_API_URL'] = 'http://localhost:8000'
        
        # 启动开发服务器
        process = subprocess.Popen(
            ['npm', 'start'],
            cwd='frontend',
            env=env
        )
        
        print("✅ 前端服务器启动成功!")
        print("🌐 访问地址: http://localhost:3000")
        print("📱 新功能:")
        print("   - 🔍 向量数据库管理: http://localhost:3000/vector")
        print("   - 👥 人类反馈管理: http://localhost:3000/feedback")
        print("   - ⚙️ 系统管理: http://localhost:3000/admin")
        print("\n按 Ctrl+C 停止服务器")
        
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 正在停止前端服务器...")
            process.terminate()
            process.wait()
            print("✅ 前端服务器已停止")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        return False

def build_frontend():
    """构建前端生产版本"""
    print("🔨 构建前端生产版本...")
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['REACT_APP_API_URL'] = 'http://localhost:8000'
        
        result = subprocess.run(['npm', 'run', 'build'], cwd='frontend', env=env, check=True)
        print("✅ 构建完成")
        print("📁 构建文件位于: frontend/build/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 Chemistry Agent 前端启动器")
    print("=" * 50)
    
    # 检查工作目录
    if not os.path.exists('frontend'):
        print("❌ 未找到frontend目录，请确保在项目根目录运行")
        return
    
    # 检查Node.js和npm
    if not check_node_installed():
        print("❌ 未安装Node.js，请先安装Node.js")
        print("   下载地址: https://nodejs.org/")
        return
    
    if not check_npm_installed():
        print("❌ 未安装npm，请先安装npm")
        return
    
    # 检查package.json
    if not os.path.exists('frontend/package.json'):
        print("❌ 未找到package.json文件")
        return
    
    print("\n📋 启动选项:")
    print("1. 启动开发服务器")
    print("2. 安装依赖")
    print("3. 构建生产版本")
    print("4. 退出")
    
    while True:
        try:
            choice = input("\n请选择 (1-4): ").strip()
            
            if choice == '1':
                start_frontend()
                break
            elif choice == '2':
                install_dependencies()
                break
            elif choice == '3':
                build_frontend()
                break
            elif choice == '4':
                print("👋 再见!")
                break
            else:
                print("❌ 无效选择，请输入1-4")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main() 