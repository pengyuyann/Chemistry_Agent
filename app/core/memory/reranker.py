'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/20 10:00
@Author  : JunYU
@File    : reranker
'''

import os
import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
import requests
from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.schema import Document

from app.core.db.models import ConversationVector, Message

@dataclass
class RerankResult:
    """重排序结果"""
    conversation_id: str
    similarity: float
    relevance_score: float
    key_entities: List[str]
    topics: List[str]
    content: str
    metadata: Dict

class Reranker:
    """重排序器，用于提升检索结果的相关性"""
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 rerank_model: str = "bge-reranker-v2-m3",
                 use_local_reranker: bool = False):
        """
        初始化重排序器
        
        Args:
            openai_api_key: OpenAI API密钥
            rerank_model: 重排序模型名称
            use_local_reranker: 是否使用本地重排序器
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.rerank_model = rerank_model
        self.use_local_reranker = use_local_reranker
        
        # 初始化嵌入模型
        if self.openai_api_key:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=self.openai_api_key,
                model="text-embedding-ada-002"
            )
        
        # 初始化本地重排序器（如果启用）
        if self.use_local_reranker:
            self._init_local_reranker()
    
    def _init_local_reranker(self):
        """初始化本地重排序器"""
        try:
            from sentence_transformers import CrossEncoder
            self.local_reranker = CrossEncoder('BAAI/bge-reranker-v2-m3')
        except ImportError:
            print("Warning: sentence-transformers not installed, falling back to API reranker")
            self.use_local_reranker = False
    
    def rerank_search_results(self, 
                            query: str, 
                            search_results: List[Tuple[ConversationVector, float]], 
                            top_k: int = 5) -> List[RerankResult]:
        """
        对搜索结果进行重排序
        
        Args:
            query: 查询文本
            search_results: 原始搜索结果 [(conversation_vector, similarity_score), ...]
            top_k: 返回结果数量
            
        Returns:
            重排序后的结果列表
        """
        if not search_results:
            return []
        
        # 准备重排序数据
        rerank_data = []
        for conv_vector, similarity in search_results:
            # 构建文档内容
            content = self._build_document_content(conv_vector)
            
            rerank_data.append({
                'conversation_id': conv_vector.conversation_id,
                'content': content,
                'similarity': similarity,
                'key_entities': json.loads(conv_vector.key_entities) if conv_vector.key_entities else [],
                'topics': json.loads(conv_vector.topics) if conv_vector.topics else [],
                'metadata': {
                    'user_id': conv_vector.user_id,
                    'created_at': conv_vector.created_at.isoformat() if conv_vector.created_at else None
                }
            })
        
        # 执行重排序
        if self.use_local_reranker:
            reranked_results = self._local_rerank(query, rerank_data)
        else:
            reranked_results = self._api_rerank(query, rerank_data)
        
        # 转换为RerankResult对象
        results = []
        for item in reranked_results[:top_k]:
            result = RerankResult(
                conversation_id=item['conversation_id'],
                similarity=item['similarity'],
                relevance_score=item['relevance_score'],
                key_entities=item['key_entities'],
                topics=item['topics'],
                content=item['content'],
                metadata=item['metadata']
            )
            results.append(result)
        
        return results
    
    def _build_document_content(self, conv_vector: ConversationVector) -> str:
        """构建文档内容用于重排序"""
        content_parts = []
        
        # 添加关键实体
        if conv_vector.key_entities:
            entities = json.loads(conv_vector.key_entities)
            if entities:
                content_parts.append(f"关键化学实体: {', '.join(entities)}")
        
        # 添加主题
        if conv_vector.topics:
            topics = json.loads(conv_vector.topics)
            if topics:
                content_parts.append(f"讨论主题: {', '.join(topics)}")
        
        # 如果有摘要嵌入，可以添加更多上下文
        # 这里可以根据需要扩展
        
        return " | ".join(content_parts) if content_parts else "化学对话记录"
    
    def _local_rerank(self, query: str, documents: List[Dict]) -> List[Dict]:
        """使用本地重排序器"""
        try:
            # 准备重排序数据
            pairs = []
            for doc in documents:
                pairs.append([query, doc['content']])
            
            # 执行重排序
            scores = self.local_reranker.predict(pairs)
            
            # 更新文档的相关性分数
            for i, doc in enumerate(documents):
                doc['relevance_score'] = float(scores[i])
            
            # 按相关性分数排序
            documents.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return documents
            
        except Exception as e:
            print(f"Local reranking failed: {e}")
            # 回退到原始相似度排序
            documents.sort(key=lambda x: x['similarity'], reverse=True)
            for doc in documents:
                doc['relevance_score'] = doc['similarity']
            return documents
    
    def _api_rerank(self, query: str, documents: List[Dict]) -> List[Dict]:
        """使用API重排序器"""
        try:
            # 这里可以集成各种重排序API，如Cohere Rerank、OpenAI等
            # 目前使用简单的启发式方法
            
            for doc in documents:
                # 计算基于关键词的相关性
                relevance_score = self._calculate_keyword_relevance(query, doc)
                doc['relevance_score'] = relevance_score
            
            # 按相关性分数排序
            documents.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return documents
            
        except Exception as e:
            print(f"API reranking failed: {e}")
            # 回退到原始相似度排序
            documents.sort(key=lambda x: x['similarity'], reverse=True)
            for doc in documents:
                doc['relevance_score'] = doc['similarity']
            return documents
    
    def _calculate_keyword_relevance(self, query: str, document: Dict) -> float:
        """计算基于关键词的相关性分数"""
        query_words = set(query.lower().split())
        content_words = set(document['content'].lower().split())
        
        # 计算关键词重叠
        overlap = len(query_words.intersection(content_words))
        
        # 考虑实体匹配
        entity_bonus = 0
        if document['key_entities']:
            entity_words = set()
            for entity in document['key_entities']:
                entity_words.update(entity.lower().split())
            entity_overlap = len(query_words.intersection(entity_words))
            entity_bonus = entity_overlap * 0.5
        
        # 考虑主题匹配
        topic_bonus = 0
        if document['topics']:
            topic_words = set()
            for topic in document['topics']:
                topic_words.update(topic.lower().split())
            topic_overlap = len(query_words.intersection(topic_words))
            topic_bonus = topic_overlap * 0.3
        
        # 综合分数
        base_score = document['similarity']
        keyword_score = (overlap + entity_bonus + topic_bonus) / max(len(query_words), 1)
        
        # 加权组合
        final_score = 0.7 * base_score + 0.3 * keyword_score
        
        return min(final_score, 1.0)
    
    def rerank_with_context(self, 
                           query: str, 
                           search_results: List[Tuple[ConversationVector, float]], 
                           conversation_context: List[Dict] = None,
                           top_k: int = 5) -> List[RerankResult]:
        """
        考虑对话上下文的重排序
        
        Args:
            query: 当前查询
            search_results: 搜索结果
            conversation_context: 当前对话上下文
            top_k: 返回结果数量
        """
        # 如果有对话上下文，增强查询
        enhanced_query = query
        if conversation_context:
            context_summary = self._summarize_context(conversation_context)
            enhanced_query = f"基于历史对话: {context_summary} | 当前问题: {query}"
        
        # 执行重排序
        reranked_results = self.rerank_search_results(enhanced_query, search_results, top_k)
        
        return reranked_results
    
    def _summarize_context(self, conversation_context: List[Dict]) -> str:
        """总结对话上下文"""
        if not conversation_context:
            return ""
        
        # 提取最近的几条消息
        recent_messages = conversation_context[-3:]  # 最近3条消息
        
        summary_parts = []
        for msg in recent_messages:
            role = msg.get('role', '')
            content = msg.get('content', '')
            if content:
                summary_parts.append(f"{role}: {content[:100]}...")
        
        return " | ".join(summary_parts)

# 全局重排序器实例
reranker = Reranker() 