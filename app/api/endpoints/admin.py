from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db.database import SessionLocal
from app.core.db import crud
from app.api.endpoints.auth import get_current_user
from app.core.db.models import User
from typing import List
from pydantic import BaseModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    class Config:
        orm_mode = True

def admin_required(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user

@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    return crud.get_users(db)

@router.post("/user/{user_id}/set_admin")
def set_admin(user_id: int, is_admin: bool, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    user = crud.set_admin(db, user_id, is_admin)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"msg": "设置成功", "user_id": user.id, "is_admin": user.is_admin}

@router.delete("/user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    user = crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"msg": "删除成功", "user_id": user_id} 