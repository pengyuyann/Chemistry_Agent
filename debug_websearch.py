#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断WebSearch工具问题的脚本
"""

import sys
import os

# 设置代理
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["https_proxy"] = "http://127.0.0.1:7897"

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_environment():
    """检查环境变量"""
    print("=== 环境变量检查 ===")
    
    # 检查代理设置
    http_proxy = os.environ.get('http_proxy')
    https_proxy = os.environ.get('https_proxy')
    print(f"HTTP代理: {http_proxy}")
    print(f"HTTPS代理: {https_proxy}")
    
    # 检查API密钥
    serp_api_key = os.environ.get('SERP_API_KEY')
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    print(f"SERP_API_KEY: {'已设置' if serp_api_key else '未设置'}")
    print(f"OPENAI_API_KEY: {'已设置' if openai_api_key else '未设置'}")
    
    return serp_api_key is not None

def test_wikipedia_search():
    """测试维基百科搜索"""
    print("\n=== 维基百科搜索测试 ===")
    try:
        from app.core.tools.search import wikipedia_search
        
        # 测试维基百科搜索
        result = wikipedia_search("aspirin")
        print(f"维基百科搜索结果: {result[:200]}...")
        return True
    except Exception as e:
        print(f"维基百科搜索失败: {e}")
        return False

def test_web_search_function():
    """测试web_search函数"""
    print("\n=== web_search函数测试 ===")
    try:
        from app.core.tools.search import web_search
        
        # 检查SERP_API_KEY
        serp_api_key = os.environ.get('SERP_API_KEY')
        if not serp_api_key:
            print("❌ SERP_API_KEY未设置，无法进行网络搜索")
            return False
        
        # 测试网络搜索
        result = web_search("chemistry news")
        print(f"网络搜索结果: {result}")
        
        if "No results" in result:
            print("❌ 网络搜索返回无结果")
            return False
        else:
            print("✅ 网络搜索成功")
            return True
            
    except Exception as e:
        print(f"❌ web_search函数测试失败: {e}")
        return False

def test_websearch_tool():
    """测试WebSearch工具"""
    print("\n=== WebSearch工具测试 ===")
    try:
        from app.core.tools.search import WebSearch
        
        # 创建WebSearch实例
        serp_api_key = os.environ.get('SERP_API_KEY')
        web_search_tool = WebSearch(serp_api_key=serp_api_key)
        
        # 测试维基百科类型查询
        print("测试维基百科类型查询...")
        wikipedia_result = web_search_tool._run("What is aspirin?")
        print(f"维基百科查询结果: {wikipedia_result[:200]}...")
        
        # 测试网络搜索类型查询
        print("测试网络搜索类型查询...")
        web_result = web_search_tool._run("latest chemistry news")
        print(f"网络搜索查询结果: {web_result[:200]}...")
        
        return True
    except Exception as e:
        print(f"❌ WebSearch工具测试失败: {e}")
        return False

def check_serpapi_connection():
    """检查SerpAPI连接"""
    print("\n=== SerpAPI连接测试 ===")
    try:
        from langchain import SerpAPIWrapper
        
        serp_api_key = os.environ.get('SERP_API_KEY')
        if not serp_api_key:
            print("❌ SERP_API_KEY未设置")
            return False
        
        # 创建SerpAPIWrapper实例
        serp_wrapper = SerpAPIWrapper(serpapi_api_key=serp_api_key)
        
        # 测试简单搜索
        result = serp_wrapper.run("test")
        print(f"SerpAPI测试结果: {result[:200]}...")
        
        if "No results" in result:
            print("❌ SerpAPI连接失败或无结果")
            return False
        else:
            print("✅ SerpAPI连接成功")
            return True
            
    except Exception as e:
        print(f"❌ SerpAPI连接测试失败: {e}")
        return False

def main():
    print("开始诊断WebSearch工具问题...")
    print("=" * 50)
    
    # 检查环境变量
    env_ok = check_environment()
    
    # 测试维基百科搜索
    wiki_ok = test_wikipedia_search()
    
    # 测试web_search函数
    web_func_ok = test_web_search_function()
    
    # 测试SerpAPI连接
    serp_ok = check_serpapi_connection()
    
    # 测试WebSearch工具
    tool_ok = test_websearch_tool()
    
    print("\n" + "=" * 50)
    print("诊断结果总结:")
    print(f"环境变量: {'✅' if env_ok else '❌'}")
    print(f"维基百科搜索: {'✅' if wiki_ok else '❌'}")
    print(f"web_search函数: {'✅' if web_func_ok else '❌'}")
    print(f"SerpAPI连接: {'✅' if serp_ok else '❌'}")
    print(f"WebSearch工具: {'✅' if tool_ok else '❌'}")
    
    if not env_ok:
        print("\n🔧 解决方案:")
        print("1. 设置SERP_API_KEY环境变量")
        print("2. 确保代理设置正确")
    
    if not serp_ok and env_ok:
        print("\n🔧 可能的解决方案:")
        print("1. 检查SERP_API_KEY是否有效")
        print("2. 检查网络连接和代理设置")
        print("3. 确认SerpAPI服务是否可用")

if __name__ == "__main__":
    main() 