import os
import pytest
from dotenv import load_dotenv

# 设置代理
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["https_proxy"] = "http://127.0.0.1:7897"

# 加载环境变量
load_dotenv()

# 导入 ChemAgent
from app.core.agents.chemagent import ChemAgent


def test_version():
    """测试版本信息"""
    # 这里可以添加版本检查
    assert True


@pytest.mark.skip(reason="This requires an api call")
def test_agent_init():
    """测试 ChemAgent 初始化"""
    chem_model = ChemAgent(
        model="deepseek-chat", 
        temp=0.1, 
        max_iterations=2, 
        openai_api_key=os.getenv("DEEPSEEK_API_KEY")
    )
    out = chem_model.run("hello")
    assert isinstance(out, str)


def test_agent_tools():
    """测试 ChemAgent 工具加载"""
    chem_model = ChemAgent(
        model="deepseek-chat",
        temp=0.1,
        max_iterations=2,
        openai_api_key=os.getenv("DEEPSEEK_API_KEY")
    )
    # 检查工具是否正确加载
    assert hasattr(chem_model, 'agent_executor')
    assert hasattr(chem_model, 'llm')
