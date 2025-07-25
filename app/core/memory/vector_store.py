import json
import numpy as np
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.core.db.models import Message, ConversationVector
import uuid
from .reranker import Reranker, RerankResult

class VectorStore:
    """向量数据库管理器"""
    
    def __init__(self, embedding_model: str = "text-embedding-ada-002", use_reranker: bool = True):
        self.embedding_model = embedding_model
        self.embeddings_cache = {}  # 简单的内存缓存
        self.use_reranker = use_reranker
        
        # 初始化重排序器
        if self.use_reranker:
            self.reranker = Reranker()
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本的向量表示"""
        # 这里应该调用实际的嵌入模型API
        # 暂时使用简单的哈希作为向量（实际应用中需要替换为真实的嵌入模型）
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # 将哈希转换为向量（1536维，模拟OpenAI的嵌入维度）
        vector = []
        for i in range(0, len(hash_hex), 2):
            if len(vector) >= 1536:
                break
            hex_pair = hash_hex[i:i+2]
            vector.append(int(hex_pair, 16) / 255.0)
        
        # 如果向量长度不够，用0填充
        while len(vector) < 1536:
            vector.append(0.0)
        
        return vector[:1536]
    
    def store_message_embedding(self, db: Session, message_id: int, content: str) -> str:
        """存储消息的向量表示"""
        embedding = self.get_embedding(content)
        vector_id = str(uuid.uuid4())
        
        # 更新消息记录
        message = db.query(Message).filter(Message.id == message_id).first()
        if message:
            message.embedding = json.dumps(embedding)
            message.embedding_model = self.embedding_model
            message.vector_id = vector_id
            db.commit()
        
        # 缓存向量
        self.embeddings_cache[vector_id] = embedding
        
        return vector_id
    
    def store_conversation_summary(self, db: Session, conversation_id: str, user_id: int, 
                                 summary: str, key_entities: List[str], topics: List[str]) -> str:
        """存储对话摘要的向量表示"""
        summary_embedding = self.get_embedding(summary)
        vector_id = str(uuid.uuid4())
        
        # 创建或更新对话向量记录
        conv_vector = db.query(ConversationVector).filter(
            ConversationVector.conversation_id == conversation_id
        ).first()
        
        if not conv_vector:
            conv_vector = ConversationVector(
                conversation_id=conversation_id,
                user_id=user_id,
                summary_embedding=json.dumps(summary_embedding),
                key_entities=json.dumps(key_entities),
                topics=json.dumps(topics)
            )
            db.add(conv_vector)
        else:
            conv_vector.summary_embedding = json.dumps(summary_embedding)
            conv_vector.key_entities = json.dumps(key_entities)
            conv_vector.topics = json.dumps(topics)
        
        db.commit()
        
        # 缓存向量
        self.embeddings_cache[vector_id] = summary_embedding
        
        return vector_id
    
    def similarity_search(self, query: str, conversation_vectors: List[ConversationVector], 
                         top_k: int = 5) -> List[Tuple[ConversationVector, float]]:
        """相似性搜索"""
        query_embedding = self.get_embedding(query)
        
        results = []
        for conv_vector in conversation_vectors:
            if conv_vector.summary_embedding:
                summary_embedding = json.loads(conv_vector.summary_embedding)
                similarity = self.cosine_similarity(query_embedding, summary_embedding)
                results.append((conv_vector, similarity))
        
        # 按相似度排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_relevant_context(self, db: Session, user_id: int, current_query: str, 
                           conversation_id: str, top_k: int = 3, 
                           conversation_context: List[Dict] = None) -> List[Dict]:
        """获取相关的历史上下文"""
        # 获取用户的所有对话向量
        conversation_vectors = db.query(ConversationVector).filter(
            ConversationVector.user_id == user_id,
            ConversationVector.conversation_id != conversation_id  # 排除当前对话
        ).all()
        
        if not conversation_vectors:
            return []
        
        # 相似性搜索
        similar_conversations = self.similarity_search(current_query, conversation_vectors, top_k * 2)  # 获取更多候选
        
        # 使用重排序器提升结果质量
        if self.use_reranker and similar_conversations:
            reranked_results = self.reranker.rerank_with_context(
                current_query, 
                similar_conversations, 
                conversation_context, 
                top_k
            )
            
            # 转换为字典格式
            relevant_context = []
            for result in reranked_results:
                context = {
                    "conversation_id": result.conversation_id,
                    "similarity": result.similarity,
                    "relevance_score": result.relevance_score,
                    "key_entities": result.key_entities,
                    "topics": result.topics,
                    "content": result.content
                }
                relevant_context.append(context)
        else:
            # 回退到原始方法
            relevant_context = []
            for conv_vector, similarity in similar_conversations[:top_k]:
                if similarity > 0.3:  # 相似度阈值
                    context = {
                        "conversation_id": conv_vector.conversation_id,
                        "similarity": similarity,
                        "relevance_score": similarity,  # 使用相似度作为相关性分数
                        "key_entities": json.loads(conv_vector.key_entities) if conv_vector.key_entities else [],
                        "topics": json.loads(conv_vector.topics) if conv_vector.topics else []
                    }
                    relevant_context.append(context)
        
        return relevant_context
    
    def update_conversation_vectors(self, db: Session, conversation_id: str, user_id: int):
        """更新对话的向量表示"""
        from app.core.db.crud import get_conversation_messages
        from app.api.endpoints.chemagent_chat import generate_conversation_summary, extract_key_topics, extract_chemical_entities
        
        # 获取对话消息
        messages = get_conversation_messages(db, conversation_id)
        
        if not messages:
            return
        
        # 生成摘要和提取关键信息
        summary = generate_conversation_summary(messages)
        topics = extract_key_topics(messages)
        entities = extract_chemical_entities(messages)
        
        # 存储向量表示
        self.store_conversation_summary(db, conversation_id, user_id, summary, entities, topics)
        
        # 为每条消息生成向量
        for message in messages:
            if not message.embedding:
                self.store_message_embedding(db, message.id, message.content)

# 全局向量存储实例
vector_store = VectorStore() 