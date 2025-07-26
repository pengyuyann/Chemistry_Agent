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
import json
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv

from fastapi import APIRouter, Body, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.memory.memory_manager import get_session_history
from app.core.memory.vector_store import vector_store
from app.core.db.database import get_db
from app.core.db.crud import (
    create_conversation, get_user_conversations, get_conversation_by_id,
    update_conversation_title, delete_conversation, add_message, get_conversation_messages,
    increment_api_calls
)
from app.core.db.models import User
from app.core.security import get_current_user

# 导入 ChemAgent
from app.core.agents import ChemAgent

# 加载环境变量
load_dotenv()

# 设置代理
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["https_proxy"] = "http://127.0.0.1:7897"

router = APIRouter()


class ChemAgentRequest(BaseModel):
    input: str = Field(..., description="用户的化学问题或任务")
    conversation_id: Optional[str] = Field(None,
                                           description="对话ID，如果不提供将自动生成")
    model: str = Field(default=os.getenv("DEFAULT_MODEL", "deepseek-chat"),
                       description="使用的LLM模型")
    tools_model: str = Field(default=os.getenv("DEFAULT_TOOLS_MODEL", "deepseek-chat"),
                             description="工具选择使用的模型")
    temperature: float = Field(default=float(os.getenv("DEFAULT_TEMPERATURE", "0.1")),
                               description="模型温度参数")
    max_iterations: int = Field(default=int(os.getenv("DEFAULT_MAX_ITERATIONS", "40")),
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
                "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
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
                openai_api_key=api_keys.get("DEEPSEEK_API_KEY"),  # 使用DeepSeek API密钥
                api_keys=api_keys,
                local_rxn=config["local_rxn"],
                user_id=config.get("user_id"),
                conversation_id=config.get("conversation_id"),
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
        "available_models": ["deepseek-chat", "deepseek-reasoner", "gpt-4-0613", "gpt-3.5-turbo-0613"],
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


from fastapi.responses import StreamingResponse

@router.post("/stream_chat")
async def chemagent_stream_chat(
    request: ChemAgentRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 记录API调用
    increment_api_calls(db, current_user.id)
    conv_id = request.conversation_id or str(uuid.uuid4())
    
    # 创建或获取对话
    conversation = get_conversation_by_id(db, conv_id)
    if not conversation:
        # 创建新对话，使用用户输入的前50个字符作为标题
        title = request.input[:50] + "..." if len(request.input) > 50 else request.input
        conversation = create_conversation(db, current_user.id, title, request.model)
        conv_id = conversation.conversation_id
    
    # 添加用户消息到数据库
    user_message = add_message(db, conv_id, "user", request.input, request.model)
    
    try:
        config = {
            "model": request.model,
            "tools_model": request.tools_model,
            "temperature": request.temperature,
            "max_iterations": request.max_iterations,
            "streaming": True,  # 强制流式
            "local_rxn": request.local_rxn,
            "api_keys": request.api_keys,
        }
        # 更新配置以包含用户信息
        config.update({
            "user_id": current_user.id,
            "conversation_id": conv_id
        })
        
        chemagent = get_chemagent_instance(config)
        
        # 获取对话上下文和历史相关对话
        conversation_context = get_conversation_messages(db, conv_id)
        conversation_context = [
            {"role": msg.role, "content": msg.content} 
            for msg in conversation_context[-6:]  # 最近3轮对话
        ]
        
        # 使用reranker获取相关历史对话
        relevant_history = vector_store.get_relevant_context(
            db, current_user.id, request.input, conv_id, top_k=3, 
            conversation_context=conversation_context
        )
        
        async def event_generator():
            chunk_count = 0
            assistant_response = ""
            
            try:
                # 使用增强的上下文提示
                enhanced_prompt = chemagent.get_enhanced_context_prompt(
                    request.input, conversation_context, relevant_history
                )
                
                async for chunk in chemagent.run_stream(enhanced_prompt):
                    chunk_count += 1
                    
                    # 解析chunk以获取最终答案
                    try:
                        chunk_data = json.loads(chunk)
                        if chunk_data.get("type") == "final":
                            assistant_response = chunk_data.get("output", "")
                    except Exception as parse_error:
                        # 如果解析失败，继续处理下一个chunk
                        pass
                    
                    yield f"data: {chunk}\n\n"
                
                # 流式输出完成后，保存助手回复到数据库
                if assistant_response:
                    assistant_message = add_message(db, conv_id, "assistant", assistant_response, request.model)
                else:
                    # 如果没有获取到最终答案，尝试从流式回调中获取
                    if hasattr(chemagent, 'streaming_callback') and chemagent.streaming_callback.tokens:
                        fallback_response = ''.join(chemagent.streaming_callback.tokens)
                        if fallback_response.strip():
                            assistant_message = add_message(db, conv_id, "assistant", fallback_response, request.model)
                
            except Exception as stream_error:
                import traceback
                traceback.print_exc()
                
                # 即使出现异常，也尝试保存助手回复
                if not assistant_response and hasattr(chemagent, 'streaming_callback') and chemagent.streaming_callback.tokens:
                    fallback_response = ''.join(chemagent.streaming_callback.tokens)
                    if fallback_response.strip():
                        try:
                            assistant_message = add_message(db, conv_id, "assistant", fallback_response, request.model)
                        except Exception as save_error:
                            print(f"[DEBUG] Failed to save fallback response: {save_error}")
                
                # 发送错误信息
                error_data = {
                    "type": "error", 
                    "message": str(stream_error)
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ChemAgent流式执行失败: {str(e)}")


# 对话历史相关API端点
@router.get("/conversations")
def get_conversations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的所有对话"""
    conversations = get_user_conversations(db, current_user.id, skip, limit)
    return {
        "conversations": [
            {
                "id": conv.conversation_id,
                "title": conv.title,
                "model_used": conv.model_used,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "message_count": len(conv.messages)
            }
            for conv in conversations
        ]
    }


@router.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取特定对话的详细信息"""
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    messages = get_conversation_messages(db, conversation_id)
    return {
        "id": conversation.conversation_id,
        "title": conversation.title,
        "model_used": conversation.model_used,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "model_used": msg.model_used,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
    }


@router.put("/conversations/{conversation_id}/title")
def update_conversation_title_api(
    conversation_id: str,
    title: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新对话标题"""
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    updated_conv = update_conversation_title(db, conversation_id, title)
    return {"message": "标题更新成功", "title": updated_conv.title}


@router.delete("/conversations/{conversation_id}")
def delete_conversation_api(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除对话"""
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    delete_conversation(db, conversation_id)
    return {"message": "对话删除成功"}


@router.get("/models")
def get_available_models():
    """获取可用的模型列表"""
    return {
        "models": [
            {
                "id": "deepseek-chat",
                "name": "DeepSeek Chat",
                "description": "通用对话模型，适合日常化学问题"
            },
            {
                "id": "deepseek-reasoner",
                "name": "DeepSeek Reasoner", 
                "description": "推理增强模型，适合复杂化学推理"
            },
            {
                "id": "gpt-4-0613",
                "name": "GPT-4",
                "description": "OpenAI GPT-4模型"
            },
            {
                "id": "gpt-3.5-turbo-0613",
                "name": "GPT-3.5 Turbo",
                "description": "OpenAI GPT-3.5 Turbo模型"
            }
        ]
    }