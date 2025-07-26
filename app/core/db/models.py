from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# 从database.py导入Base，避免重复定义
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)  # 用户邮箱
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    
    # API使用情况统计
    api_calls_count = Column(Integer, default=0)  # 总API调用次数
    api_calls_today = Column(Integer, default=0)  # 今日API调用次数
    last_api_call = Column(DateTime, nullable=True)  # 最后一次API调用时间
    api_usage_reset_date = Column(DateTime, default=datetime.utcnow)  # API使用重置日期
    
    # 用户设置
    preferred_model = Column(String, default='deepseek-chat')  # 默认模型
    max_conversations = Column(Integer, default=100)  # 最大对话数量
    max_messages_per_conversation = Column(Integer, default=1000)  # 每个对话最大消息数
    
    # 用户状态
    is_active = Column(Boolean, default=True)  # 用户是否激活
    last_login = Column(DateTime, nullable=True)  # 最后登录时间
    
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

class HumanFeedback(Base):
    __tablename__ = "human_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(String, unique=True, index=True)
    request_type = Column(String)  # 请求类型
    task_description = Column(Text)  # 任务描述
    risk_assessment = Column(Text)  # 风险评估
    questions = Column(Text)  # JSON格式的问题列表
    status = Column(String, default="pending")  # pending, approved, rejected, timeout
    expert_name = Column(String, nullable=True)  # 专家姓名
    expert_message = Column(Text, nullable=True)  # 专家反馈消息
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 