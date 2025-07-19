'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/19 11:45
@Author  : JunYU
@File    : chemagent_chat
'''
'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/19 11:45
@Author  : JunYU
@File    : chemagent_chat
'''
import uuid
from typing import Optional, Dict, Any, List
import os

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

from app.core.memory.memory_manager import get_session_history

# 导入 ChemAgent
from app.core.agents import ChemAgent

router = APIRouter()


class ChemAgentRequest(BaseModel):
    input: str = Field(..., description="用户的化学问题或任务")
    conversation_id: Optional[str] = Field(None,
                                           description="对话ID，如果不提供将自动生成")
    model: str = Field(default="gpt-4-0613",
                       description="使用的LLM模型")
    tools_model: str = Field(default="gpt-3.5-turbo-0613",
                             description="工具选择使用的模型")
    temperature: float = Field(default=0.1,
                               description="模型温度参数")
    max_iterations: int = Field(default=40,
                                description="最大迭代次数")
    streaming: bool = Field(default=False,
                            description="是否使用流式输出")
    local_rxn: bool = Field(default=False,
                            description="是否使用本地反应工具")
    api_keys: Dict[str, str] = Field(default={},
                                     description="API密钥配置")


class ChemAgentResponse(BaseModel):
    output: str = Field(..., description="ChemAgent的回答")
    conversation_id: str = Field(..., description="对话ID")
    model_used: str = Field(..., description="使用的模型")
    iterations: Optional[int] = Field(None, description="实际迭代次数")


# 全局 ChemAgent 实例缓存
_chemagent_instances: Dict[str, ChemAgent] = {}


def get_chemagent_instance(config: Dict[str, Any]) -> ChemAgent:
    """获取或创建 ChemAgent 实例"""
    # 创建配置的唯一标识
    config_key = f"{config['model']}_{config['tools_model']}_{config['temperature']}_{config['local_rxn']}"

    if config_key not in _chemagent_instances:
        try:
            # 从环境变量获取 API 密钥
            api_keys = {
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                "SERP_API_KEY": os.getenv("SERP_API_KEY"),
                "RXN4CHEM_API_KEY": os.getenv("RXN4CHEM_API_KEY"),
                "CHEMSPACE_API_KEY": os.getenv("CHEMSPACE_API_KEY"),
                "SEMANTIC_SCHOLAR_API_KEY": os.getenv("SEMANTIC_SCHOLAR_API_KEY"),
            }

            # 合并用户提供的 API 密钥
            api_keys.update(config.get("api_keys", {}))

            # 创建 ChemAgent 实例
            chemagent = ChemAgent(
                model=config["model"],
                tools_model=config["tools_model"],
                temp=config["temperature"],
                max_iterations=config["max_iterations"],
                streaming=config["streaming"],
                openai_api_key=api_keys.get("OPENAI_API_KEY"),
                api_keys=api_keys,
                local_rxn=config["local_rxn"],
            )

            _chemagent_instances[config_key] = chemagent

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize ChemAgent: {str(e)}")

    return _chemagent_instances[config_key]


@router.post("/", response_model=ChemAgentResponse)
def chemagent_chat(request: ChemAgentRequest = Body(...)):
    """
    处理 ChemAgent 化学智能体聊天请求
    支持各种化学任务：分子分析、合成规划、安全性检查等
    """
    conv_id = request.conversation_id or str(uuid.uuid4())
    print(f"--- ChemAgent Chat endpoint called for conversation_id: {conv_id} ---")

    try:
        # 获取 ChemAgent 实例
        config = {
            "model": request.model,
            "tools_model": request.tools_model,
            "temperature": request.temperature,
            "max_iterations": request.max_iterations,
            "streaming": request.streaming,
            "local_rxn": request.local_rxn,
            "api_keys": request.api_keys,
        }

        chemagent = get_chemagent_instance(config)

        # 执行 ChemAgent 任务
        result = chemagent.run(request.input)

        return ChemAgentResponse(
            output=result,
            conversation_id=conv_id,
            model_used=request.model,
            iterations=None  # ChemAgent 不直接提供迭代次数
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ChemAgent execution failed: {str(e)}")


@router.get("/health")
def chemagent_health_check():
    """ChemAgent 健康检查端点"""
    return {
        "status": "ok",
        "message": "ChemAgent endpoint is ready",
        "available_models": ["gpt-4-0613", "gpt-3.5-turbo-0613"],
        "features": [
            "分子分析",
            "合成规划",
            "安全性检查",
            "文献搜索",
            "专利查询",
            "反应预测"
        ]
    }


@router.get("/tools")
def get_available_tools():
    """获取可用的化学工具列表"""
    return {
        "molecular_analysis": [
            "SMILES2Weight - 计算分子量",
            "FuncGroups - 识别官能团",
            "MolSimilarity - 计算分子相似性",
            "Query2SMILES - 分子名称转SMILES"
        ],
        "safety_check": [
            "ExplosiveCheck - 检查爆炸性",
            "ControlChemCheck - 检查管制化学品",
            "SafetySummary - 生成安全性总结"
        ],
        "synthesis": [
            "RXNPredict - 反应产物预测",
            "RXNRetrosynthesis - 逆合成分析"
        ],
        "information": [
            "WebSearch - 网络搜索",
            "LiteratureSearch - 学术文献搜索",
            "PatentCheck - 专利检查"
        ]
    }