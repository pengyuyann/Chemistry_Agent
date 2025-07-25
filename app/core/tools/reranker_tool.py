'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/20 10:30
@Author  : JunYU
@File    : reranker_tool
'''

from typing import List, Dict, Optional
from langchain.tools import BaseTool
from sqlalchemy.orm import Session
from app.core.memory.vector_store import vector_store
from app.core.db.database import SessionLocal
from app.core.db.crud import get_user_conversations
import json

class RerankerSearchTool(BaseTool):
    """重排序搜索工具，用于在对话过程中搜索相关历史对话"""
    
    name = "RerankerSearch"
    description = """
    搜索用户的历史对话记录，找到与当前问题最相关的历史对话。
    这个工具使用先进的重排序技术，能够更准确地找到相关的历史对话。
    
    输入格式：搜索查询文本
    输出：相关历史对话的详细信息，包括相关性分数、主题、关键实体等
    """
    
    def __init__(self, user_id: Optional[int] = None):
        super().__init__()
        self.user_id = user_id
    
    def _run(self, query: str) -> str:
        """执行重排序搜索"""
        try:
            if not self.user_id:
                return "错误：未指定用户ID，无法执行搜索"
            
            db = SessionLocal()
            try:
                # 获取用户的所有对话
                conversations = get_user_conversations(db, self.user_id, skip=0, limit=100)
                
                if not conversations:
                    return "未找到历史对话记录"
                
                # 使用重排序器搜索相关对话
                relevant_history = vector_store.get_relevant_context(
                    db, self.user_id, query, "", top_k=5
                )
                
                if not relevant_history:
                    return "未找到相关的历史对话"
                
                # 格式化结果
                result_parts = []
                for i, hist in enumerate(relevant_history, 1):
                    relevance_score = hist.get('relevance_score', 0)
                    similarity = hist.get('similarity', 0)
                    topics = hist.get('topics', [])
                    entities = hist.get('key_entities', [])
                    content = hist.get('content', '')
                    
                    result_parts.append(f"相关对话 {i}:")
                    result_parts.append(f"  对话ID: {hist['conversation_id']}")
                    result_parts.append(f"  相关性分数: {relevance_score:.3f}")
                    result_parts.append(f"  相似度: {similarity:.3f}")
                    
                    if topics:
                        result_parts.append(f"  讨论主题: {', '.join(topics)}")
                    if entities:
                        result_parts.append(f"  关键实体: {', '.join(entities)}")
                    if content:
                        result_parts.append(f"  内容摘要: {content}")
                    
                    result_parts.append("")
                
                return "\n".join(result_parts)
                
            finally:
                db.close()
                
        except Exception as e:
            return f"搜索过程中出现错误: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """异步执行重排序搜索"""
        return self._run(query)

class ContextEnhancementTool(BaseTool):
    """上下文增强工具，用于增强当前对话的上下文"""
    
    name = "ContextEnhancement"
    description = """
    基于当前对话内容，搜索并整合相关的历史对话信息，增强对话的上下文理解。
    这个工具可以帮助提供更连贯和个性化的回答。
    
    输入格式：当前对话内容或问题
    输出：增强的上下文信息，包括相关历史对话的摘要
    """
    
    def __init__(self, user_id: Optional[int] = None, conversation_id: Optional[str] = None):
        super().__init__()
        self.user_id = user_id
        self.conversation_id = conversation_id
    
    def _run(self, current_context: str) -> str:
        """执行上下文增强"""
        try:
            if not self.user_id:
                return "错误：未指定用户ID，无法执行上下文增强"
            
            db = SessionLocal()
            try:
                # 使用重排序器获取相关历史
                relevant_history = vector_store.get_relevant_context(
                    db, self.user_id, current_context, self.conversation_id or "", 
                    top_k=3, conversation_context=None
                )
                
                if not relevant_history:
                    return "未找到相关的历史对话来增强上下文"
                
                # 构建增强的上下文
                enhanced_context = []
                enhanced_context.append("基于历史对话的上下文增强:")
                enhanced_context.append("")
                
                for i, hist in enumerate(relevant_history, 1):
                    relevance_score = hist.get('relevance_score', 0)
                    topics = hist.get('topics', [])
                    entities = hist.get('key_entities', [])
                    
                    enhanced_context.append(f"相关历史 {i} (相关性: {relevance_score:.2f}):")
                    if topics:
                        enhanced_context.append(f"  主题: {', '.join(topics)}")
                    if entities:
                        enhanced_context.append(f"  实体: {', '.join(entities)}")
                    enhanced_context.append("")
                
                enhanced_context.append("建议：基于这些历史对话，可以提供更个性化和连贯的回答。")
                
                return "\n".join(enhanced_context)
                
            finally:
                db.close()
                
        except Exception as e:
            return f"上下文增强过程中出现错误: {str(e)}"
    
    async def _arun(self, current_context: str) -> str:
        """异步执行上下文增强"""
        return self._run(current_context)

def make_reranker_tools(user_id: Optional[int] = None, conversation_id: Optional[str] = None) -> List[BaseTool]:
    """创建重排序相关工具"""
    tools = [
        RerankerSearchTool(user_id=user_id),
        ContextEnhancementTool(user_id=user_id, conversation_id=conversation_id)
    ]
    return tools 