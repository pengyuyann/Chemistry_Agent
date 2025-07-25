from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# 从database.py导入Base，避免重复定义
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    model_used = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)  # "user" 或 "assistant"
    content = Column(Text)
    model_used = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 向量存储相关字段
    embedding = Column(Text, nullable=True)  # 存储JSON格式的向量
    embedding_model = Column(String, nullable=True)  # 使用的嵌入模型
    vector_id = Column(String, nullable=True)  # 向量数据库中的ID
    
    # 关系
    conversation = relationship("Conversation", back_populates="messages")

class ConversationVector(Base):
    __tablename__ = "conversation_vectors"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    summary_embedding = Column(Text, nullable=True)  # 对话摘要的向量
    key_entities = Column(Text, nullable=True)  # JSON格式的关键实体
    topics = Column(Text, nullable=True)  # JSON格式的话题标签
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 