from sqlalchemy.orm import Session
from .models import User, Conversation, Message
from app.core.security import get_password_hash
import uuid
from datetime import datetime, date

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, username: str, password: str, is_admin: bool = False):
    hashed_password = get_password_hash(password)
    user = User(username=username, hashed_password=hashed_password, is_admin=is_admin)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def set_admin(db: Session, user_id: int, is_admin: bool):
    user = get_user(db, user_id)
    if user:
        user.is_admin = is_admin
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
    return user

# 对话历史相关CRUD操作
def create_conversation(db: Session, user_id: int, title: str, model_used: str):
    """创建新对话"""
    conversation_id = str(uuid.uuid4())
    conversation = Conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        title=title,
        model_used=model_used
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def get_conversation_by_id(db: Session, conversation_id: str):
    """根据对话ID获取对话"""
    return db.query(Conversation).filter(Conversation.conversation_id == conversation_id).first()

def get_user_conversations(db: Session, user_id: int, skip: int = 0, limit: int = 50):
    """获取用户的所有对话"""
    return db.query(Conversation).filter(Conversation.user_id == user_id)\
        .order_by(Conversation.updated_at.desc())\
        .offset(skip).limit(limit).all()

def update_conversation_title(db: Session, conversation_id: str, title: str):
    """更新对话标题"""
    conversation = get_conversation_by_id(db, conversation_id)
    if conversation:
        conversation.title = title
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)
    return conversation

def delete_conversation(db: Session, conversation_id: str):
    """删除对话"""
    conversation = get_conversation_by_id(db, conversation_id)
    if conversation:
        db.delete(conversation)
        db.commit()
    return conversation

def add_message(db: Session, conversation_id: str, role: str, content: str, model_used: str = None, steps: list = None):
    """添加消息到对话"""
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        return None
    
    message = Message(
        conversation_id=conversation.id,
        role=role,
        content=content,
        model_used=model_used,
        steps=steps
    )
    db.add(message)
    
    # 更新对话的更新时间
    conversation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(message)
    
    # 存储消息的向量表示
    try:
        from app.core.memory.vector_store import vector_store
        vector_store.store_message_embedding(db, message.id, content)
    except Exception as e:
        print(f"Warning: Failed to store message embedding: {e}")
    
    return message

def get_conversation_messages(db: Session, conversation_id: str):
    """获取对话的所有消息"""
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        return []
    
    return db.query(Message).filter(Message.conversation_id == conversation.id)\
        .order_by(Message.created_at.asc()).all()

# 用户个人信息相关CRUD操作
def update_user_email(db: Session, user_id: int, email: str):
    """更新用户邮箱"""
    user = get_user(db, user_id)
    if user:
        user.email = email
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user

def update_user_preferences(db: Session, user_id: int, preferred_model: str = None, 
                          max_conversations: int = None, max_messages_per_conversation: int = None):
    """更新用户偏好设置"""
    user = get_user(db, user_id)
    if user:
        if preferred_model is not None:
            user.preferred_model = preferred_model
        if max_conversations is not None:
            user.max_conversations = max_conversations
        if max_messages_per_conversation is not None:
            user.max_messages_per_conversation = max_messages_per_conversation
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user

def increment_api_calls(db: Session, user_id: int):
    """增加API调用次数"""
    user = get_user(db, user_id)
    if user:
        # 检查是否需要重置今日计数
        today = date.today()
        if user.api_usage_reset_date and user.api_usage_reset_date.date() < today:
            user.api_calls_today = 0
            user.api_usage_reset_date = datetime.utcnow()
        
        user.api_calls_count += 1
        user.api_calls_today += 1
        user.last_api_call = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user

def update_last_login(db: Session, user_id: int):
    """更新最后登录时间"""
    user = get_user(db, user_id)
    if user:
        user.last_login = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user

def get_user_stats(db: Session, user_id: int):
    """获取用户统计信息"""
    user = get_user(db, user_id)
    if not user:
        return None
    
    # 获取用户的对话和消息统计
    conversation_count = db.query(Conversation).filter(Conversation.user_id == user_id).count()
    message_count = db.query(Message).join(Conversation).filter(Conversation.user_id == user_id).count()
    
    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_active": user.is_active,
        "api_calls_count": user.api_calls_count,
        "api_calls_today": user.api_calls_today,
        "last_api_call": user.last_api_call,
        "preferred_model": user.preferred_model,
        "max_conversations": user.max_conversations,
        "max_messages_per_conversation": user.max_messages_per_conversation,
        "last_login": user.last_login,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "conversation_count": conversation_count,
        "message_count": message_count
    }

def create_user_with_email(db: Session, username: str, email: str, password: str, is_admin: bool = False):
    """创建包含邮箱的用户"""
    hashed_password = get_password_hash(password)
    user = User(
        username=username, 
        email=email,
        hashed_password=hashed_password, 
        is_admin=is_admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user