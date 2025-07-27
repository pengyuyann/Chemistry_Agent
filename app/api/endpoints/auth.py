from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import re

from app.core.db.database import get_db
from app.core.db.crud import (
    get_user_by_username, 
    create_user, 
    get_user,
    update_user_email,
    update_user_preferences,
    get_user_stats,
    update_last_login,
    increment_api_calls,
    create_user_with_email
)
from app.core.security import verify_password, create_access_token, get_current_user, decode_access_token
from app.core.db.models import User

router = APIRouter()

# JWT配置
SECRET_KEY = "your-secret-key-here"  # 在生产环境中应该使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserCreate(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    class Config:
        from_attributes = True

@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )
    
    # 如果提供了邮箱，检查邮箱是否已存在
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="邮箱已被使用"
            )
    
    # 创建用户
    if user_data.email:
        user = create_user_with_email(db, user_data.username, user_data.email, user_data.password)
    else:
        user = create_user(db, user_data.username, user_data.password)
    
    return {"message": "用户注册成功", "user_id": user.id}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 更新最后登录时间
    update_last_login(db, user.id)
    
    access_token = create_access_token({
        "sub": user.username, 
        "user_id": user.id, 
        "is_admin": user.is_admin
    })
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user 

@router.get("/profile")
def get_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取用户个人信息"""
    user_stats = get_user_stats(db, current_user.id)
    if not user_stats:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return user_stats

class EmailUpdateRequest(BaseModel):
    email: str
    
    @validator('email')
    def validate_email(cls, v):
        if not v:
            raise ValueError('邮箱不能为空')
        # 简单的邮箱格式验证
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('邮箱格式不正确')
        return v
    
    class Config:
        from_attributes = True

@router.put("/profile/email")
def update_email(request: EmailUpdateRequest = Body(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """更新用户邮箱"""
    # 检查邮箱是否已被其他用户使用
    existing_email = db.query(User).filter(User.email == request.email, User.id != current_user.id).first()
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="邮箱已被其他用户使用"
        )
    
    user = update_user_email(db, current_user.id, request.email)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {"message": "邮箱更新成功", "email": user.email}

@router.put("/profile/preferences")
def update_preferences(
    preferred_model: Optional[str] = None,
    max_conversations: Optional[int] = None,
    max_messages_per_conversation: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户偏好设置"""
    user = update_user_preferences(
        db, 
        current_user.id, 
        preferred_model, 
        max_conversations, 
        max_messages_per_conversation
    )
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "message": "偏好设置更新成功",
        "preferred_model": user.preferred_model,
        "max_conversations": user.max_conversations,
        "max_messages_per_conversation": user.max_messages_per_conversation
    }

@router.get("/usage")
def get_api_usage(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取API使用情况"""
    user_stats = get_user_stats(db, current_user.id)
    if not user_stats:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "api_calls_count": user_stats["api_calls_count"],
        "api_calls_today": user_stats["api_calls_today"],
        "last_api_call": user_stats["last_api_call"],
        "usage_reset_date": user_stats.get("api_usage_reset_date")
    }
