#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Chemistry Agent API 测试脚本
用于测试与 ChemAgent 的交互功能
"""

import requests
import json
import time
import os

# 设置代理
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["https_proxy"] = "http://127.0.0.1:7897"

# API 基础URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")

def test_api_info():
    """测试API信息"""
    print("\n📋 测试API信息...")
    try:
        response = requests.get(f"{BASE_URL}/api/info")
        if response.status_code == 200:
            print("✅ API信息获取成功")
            info = response.json()
            print(f"API名称: {info['name']}")
            print(f"版本: {info['version']}")
            print(f"功能: {', '.join(info['features'])}")
        else:
            print(f"❌ API信息获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ API信息获取异常: {e}")

def test_chemagent_health():
    """测试ChemAgent健康检查"""
    print("\n🧪 测试ChemAgent健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/api/chemagent/health")
        if response.status_code == 200:
            print("✅ ChemAgent健康检查通过")
            print(f"响应: {response.json()}")
        else:
            print(f"❌ ChemAgent健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ ChemAgent健康检查异常: {e}")

def test_chemagent_tools():
    """测试ChemAgent工具列表"""
    print("\n🛠️ 测试ChemAgent工具列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/chemagent/tools")
        if response.status_code == 200:
            print("✅ ChemAgent工具列表获取成功")
            tools = response.json()
            for category, tool_list in tools.items():
                print(f"\n{category}:")
                for tool in tool_list:
                    print(f"  - {tool}")
        else:
            print(f"❌ ChemAgent工具列表获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ ChemAgent工具列表获取异常: {e}")

def test_chemagent_chat(question: str):
    """测试ChemAgent聊天功能"""
    print(f"\n💬 测试ChemAgent聊天功能...")
    print(f"问题: {question}")
    
    # 准备请求数据
    payload = {
        "input": question,
        "model": "deepseek-chat",
        "tools_model": "deepseek-chat",
        "temperature": 0.1,
        "max_iterations": 10,
        "streaming": False,
        "local_rxn": False,
        "api_keys": {}
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/chemagent/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        if response.status_code == 200:
            print("✅ ChemAgent聊天成功")
            result = response.json()
            print(f"对话ID: {result['conversation_id']}")
            print(f"使用模型: {result['model_used']}")
            print(f"响应时间: {end_time - start_time:.2f}秒")
            print(f"回答: {result['output']}")
        else:
            print(f"❌ ChemAgent聊天失败: {response.status_code}")
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"❌ ChemAgent聊天异常: {e}")

def main():
    """主测试函数"""
    print("🧪 Chemistry Agent API 测试开始")
    print("=" * 50)
    
    # 基础测试
    test_health_check()
    test_api_info()
    test_chemagent_health()
    test_chemagent_tools()
    
    # 聊天测试
    test_questions = [
        "计算苯的分子量",
        "什么是SMILES格式？",
        "请分析乙醇的化学性质",
        "如何合成阿司匹林？"
    ]
    
    for question in test_questions:
        test_chemagent_chat(question)
        print("\n" + "-" * 50)
        time.sleep(2)  # 避免请求过于频繁
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main() 