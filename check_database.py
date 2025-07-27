#!/usr/bin/env python3
"""
检查数据库连接和表结构
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import inspect
from app.core.db.database import engine, get_db
from app.core.db.models import User, Conversation, Message

def check_database():
    """检查数据库连接和表结构"""
    try:
        print("=== 检查数据库连接 ===")
        
        # 检查数据库连接
        with engine.connect() as conn:
            print("✅ 数据库连接成功")
        
        # 检查表结构
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"✅ 数据库中的表: {tables}")
        
        # 检查用户表结构
        if 'users' in tables:
            columns = inspector.get_columns('users')
            print("\n用户表结构:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        
        # 检查用户数据
        db = next(get_db())
        try:
            users = db.query(User).all()
            print(f"\n数据库中的用户数量: {len(users)}")
            for user in users:
                print(f"  - {user.username} (ID: {user.id}, 管理员: {user.is_admin})")
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return False

if __name__ == "__main__":
    check_database()