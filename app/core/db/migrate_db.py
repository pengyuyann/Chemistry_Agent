#!/usr/bin/env python3
"""
数据库迁移脚本
用于更新现有数据库结构以支持向量存储
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from app.core.db.database import DATABASE_URL
from app.core.db.models import Base, User, Conversation, Message, ConversationVector

def migrate_database():
    """迁移数据库，添加新的用户字段"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("PRAGMA table_info(users)"))
        existing_columns = [row[1] for row in result.fetchall()]
        
        # 需要添加的字段
        new_columns = [
            ("email", "TEXT"),
            ("api_calls_count", "INTEGER DEFAULT 0"),
            ("api_calls_today", "INTEGER DEFAULT 0"),
            ("last_api_call", "DATETIME"),
            ("api_usage_reset_date", "DATETIME"),
            ("preferred_model", "TEXT DEFAULT 'deepseek-chat'"),
            ("max_conversations", "INTEGER DEFAULT 100"),
            ("max_messages_per_conversation", "INTEGER DEFAULT 1000"),
            ("is_active", "BOOLEAN DEFAULT 1"),
            ("last_login", "DATETIME")
        ]
        
        # 添加缺失的字段
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                try:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"))
                    print(f"✅ 已添加字段: {column_name}")
                except Exception as e:
                    print(f"❌ 添加字段 {column_name} 失败: {e}")
        
        conn.commit()
        print("数据库迁移完成！")

def check_database_status():
    """检查数据库状态"""
    print("检查数据库状态...")
    
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    tables = inspector.get_table_names()
    print(f"数据库中的表: {tables}")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 检查各表的记录数
        for table_name in tables:
            if table_name == 'users':
                count = db.query(User).count()
                print(f"  {table_name}: {count} 条记录")
            elif table_name == 'conversations':
                count = db.query(Conversation).count()
                print(f"  {table_name}: {count} 条记录")
            elif table_name == 'messages':
                count = db.query(Message).count()
                print(f"  {table_name}: {count} 条记录")
            elif table_name == 'conversation_vectors':
                count = db.query(ConversationVector).count()
                print(f"  {table_name}: {count} 条记录")
        
        # 检查向量存储状态
        if 'conversation_vectors' in tables:
            vectors = db.query(ConversationVector).limit(5).all()
            print(f"  向量存储示例:")
            for vec in vectors:
                print(f"    对话ID: {vec.conversation_id}, 用户ID: {vec.user_id}")
        
    except Exception as e:
        print(f"检查失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库迁移工具")
    parser.add_argument("--migrate", default=1, action="store_true", help="执行数据库迁移")
    parser.add_argument("--check", action="store_true", help="检查数据库状态")
    
    args = parser.parse_args()
    
    if args.migrate:
        migrate_database()
    elif args.check:
        check_database_status()
    else:
        print("请指定操作: --migrate 或 --check")
        print("示例:")
        print("  python migrate_db.py --migrate")
        print("  python migrate_db.py --check") 