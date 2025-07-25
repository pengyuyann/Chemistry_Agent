from sqlalchemy.orm import Session
from .models import User, Conversation, Message
from app.core.security import get_password_hash
import uuid
from datetime import datetime

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

def add_message(db: Session, conversation_id: str, role: str, content: str, model_used: str = None):
    """添加消息到对话"""
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        return None
    
    message = Message(
        conversation_id=conversation.id,
        role=role,
        content=content,
        model_used=model_used
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