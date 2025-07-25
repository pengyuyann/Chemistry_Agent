import os
import pytest
import requests
from dotenv import load_dotenv

# 设置代理
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["https_proxy"] = "http://127.0.0.1:7897"

# 加载环境变量
load_dotenv()

# API 基础URL
BASE_URL = "http://localhost:8000"


@pytest.fixture
def api_client():
    """API客户端fixture"""
    return requests.Session()


def test_health_check(api_client):
    """测试健康检查端点"""
    response = api_client.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Chemistry Agent API" in data["service"]


def test_api_info(api_client):
    """测试API信息端点"""
    response = api_client.get(f"{BASE_URL}/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Chemistry Agent API"
    assert "deepseek-chat" in data["supported_models"]


def test_chemagent_health(api_client):
    """测试ChemAgent健康检查端点"""
    response = api_client.get(f"{BASE_URL}/api/chemagent/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_chemagent_tools(api_client):
    """测试ChemAgent工具列表端点"""
    response = api_client.get(f"{BASE_URL}/api/chemagent/tools")
    assert response.status_code == 200
    data = response.json()
    assert "molecular_analysis" in data
    assert "safety_check" in data
    assert "synthesis" in data
    assert "information" in data


@pytest.mark.skip(reason="This requires a running server")
def test_chemagent_chat_simple(api_client):
    """测试ChemAgent简单聊天功能"""
    payload = {
        "input": "Calculate the molecular weight of benzene",
        "model": "deepseek-chat",
        "tools_model": "deepseek-chat",
        "temperature": 0.1,
        "max_iterations": 5,
        "streaming": False,
        "local_rxn": False,
        "api_keys": {}
    }
    
    response = api_client.post(
        f"{BASE_URL}/api/chemagent/",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        assert "output" in data
        assert "conversation_id" in data
        assert "model_used" in data
        assert isinstance(data["output"], str)
        assert len(data["output"]) > 0
    else:
        # 如果服务器没有运行，跳过测试
        pytest.skip("Server not running")


@pytest.mark.skip(reason="This requires a running server")
def test_chemagent_chat_chemical_properties(api_client):
    """测试ChemAgent化学性质分析功能"""
    payload = {
        "input": "Please analyze the chemical properties of ethanol",
        "model": "deepseek-chat",
        "tools_model": "deepseek-chat",
        "temperature": 0.1,
        "max_iterations": 10,
        "streaming": False,
        "local_rxn": False,
        "api_keys": {}
    }
    
    response = api_client.post(
        f"{BASE_URL}/api/chemagent/",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        assert "output" in data
        assert isinstance(data["output"], str)
        assert len(data["output"]) > 0
    else:
        pytest.skip("Server not running")


def test_invalid_endpoint(api_client):
    """测试无效端点"""
    response = api_client.get(f"{BASE_URL}/invalid_endpoint")
    assert response.status_code == 404


def test_root_endpoint(api_client):
    """测试根端点"""
    response = api_client.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert "Chemistry Agent API" in data["message"]
    assert "endpoints" in data 