#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
环境变量检查脚本
用于检查Chemistry Agent API所需的环境变量是否已正确设置
"""

import os
import sys

def check_environment_variables():
    """检查环境变量"""
    print("🔍 检查 Chemistry Agent API 环境变量...")
    print("=" * 50)
    
    # 必需的环境变量
    required_vars = {
        "DEEPSEEK_API_KEY": "DeepSeek API密钥（必需）"
    }
    
    # 可选的环境变量
    optional_vars = {
        "SERP_API_KEY": "SERP API密钥（可选）",
        "RXN4CHEM_API_KEY": "RXN4Chem API密钥（可选）",
        "CHEMSPACE_API_KEY": "ChemSpace API密钥（可选）",
        "SEMANTIC_SCHOLAR_API_KEY": "Semantic Scholar API密钥（可选）"
    }
    
    all_good = True
    
    # 检查必需的环境变量
    print("📋 必需的环境变量:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # 隐藏API密钥的大部分内容，只显示前4位和后4位
            masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
            print(f"  ✅ {var}: {masked_value}")
        else:
            print(f"  ❌ {var}: 未设置 - {description}")
            all_good = False
    
    print()
    
    # 检查可选的环境变量
    print("📋 可选的环境变量:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
            print(f"  ✅ {var}: {masked_value}")
        else:
            print(f"  ⚪ {var}: 未设置 - {description}")
    
    print()
    
    # 总结
    if all_good:
        print("🎉 所有必需的环境变量都已设置！")
        print("✅ 可以启动 Chemistry Agent API 了")
    else:
        print("⚠️  缺少必需的环境变量")
        print("请设置以下环境变量：")
        print()
        
        if sys.platform.startswith('win'):
            print("Windows PowerShell:")
            print("$env:DEEPSEEK_API_KEY = 'your_deepseek_api_key'")
            print()
            print("Windows CMD:")
            print("set DEEPSEEK_API_KEY=your_deepseek_api_key")
            print()
            print("或运行 setup_env_windows.bat 脚本")
        else:
            print("Linux/Mac:")
            print("export DEEPSEEK_API_KEY='your_deepseek_api_key'")
    
    return all_good

def test_api_connection():
    """测试API连接"""
    print("\n🧪 测试API连接...")
    
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key:
        print("❌ 无法测试：DEEPSEEK_API_KEY 未设置")
        return False
    
    try:
        import requests
        
        # 测试DeepSeek API连接
        headers = {
            "Authorization": f"Bearer {deepseek_key}",
            "Content-Type": "application/json"
        }
        
        # 简单的API测试
        response = requests.get(
            "https://api.deepseek.com/v1/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ DeepSeek API 连接成功")
            return True
        else:
            print(f"❌ DeepSeek API 连接失败: {response.status_code}")
            return False
            
    except ImportError:
        print("❌ 无法测试：缺少 requests 库")
        print("请运行: pip install requests")
        return False
    except Exception as e:
        print(f"❌ API 连接测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 Chemistry Agent API 环境检查")
    print("=" * 50)
    
    # 检查环境变量
    env_ok = check_environment_variables()
    
    # 如果环境变量都设置了，测试API连接
    if env_ok:
        test_api_connection()
    
    print("\n" + "=" * 50)
    print("检查完成！")

if __name__ == "__main__":
    main() 