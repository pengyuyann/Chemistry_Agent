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
    """执行数据库迁移"""
    print("开始数据库迁移...")
    
    # 创建数据库引擎
    engine = create_engine(DATABASE_URL)
    
    # 检查是否需要创建新表
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print(f"现有表: {existing_tables}")
    
    # 创建所有表（如果不存在）
    Base.metadata.create_all(bind=engine)
    
    # 检查并添加缺失的列
    try:
        # 检查users表是否有updated_at列
        user_columns = inspector.get_columns('users')
        user_column_names = [col['name'] for col in user_columns]
        
        if 'updated_at' not in user_column_names:
            print("添加缺失的updated_at列到users表...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN updated_at DATETIME"))
                conn.commit()
            print("updated_at列添加成功")
        
        # 检查messages表是否有向量相关列
        message_columns = inspector.get_columns('messages')
        message_column_names = [col['name'] for col in message_columns]
        print(f"当前messages表列: {message_column_names}")
        
        missing_message_columns = []
        if 'embedding' not in message_column_names:
            missing_message_columns.append("embedding TEXT")
        if 'embedding_model' not in message_column_names:
            missing_message_columns.append("embedding_model VARCHAR")
        if 'vector_id' not in message_column_names:
            missing_message_columns.append("vector_id VARCHAR")
        
        if missing_message_columns:
            print(f"添加缺失的向量相关列到messages表: {missing_message_columns}")
            with engine.connect() as conn:
                for column_def in missing_message_columns:
                    try:
                        print(f"  添加列: {column_def}")
                        conn.execute(text(f"ALTER TABLE messages ADD COLUMN {column_def}"))
                    except Exception as col_error:
                        print(f"  添加列 {column_def} 时出错: {col_error}")
                conn.commit()
            print("向量相关列添加完成")
        else:
            print("messages表已包含所有必要的向量相关列")
    except Exception as e:
        print(f"添加列时出错: {e}")
    
    # 检查新表是否创建成功
    inspector = inspect(engine)
    updated_tables = inspector.get_table_names()
    
    print(f"更新后的表: {updated_tables}")
    
    # 检查新添加的列
    if 'messages' in updated_tables:
        message_columns = inspector.get_columns('messages')
        print(f"Messages表列: {[col['name'] for col in message_columns]}")
    
    if 'conversation_vectors' in updated_tables:
        vector_columns = inspector.get_columns('conversation_vectors')
        print(f"ConversationVectors表列: {[col['name'] for col in vector_columns]}")
    
    print("数据库迁移完成！")
    
    # 创建会话并测试连接
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 测试查询
        user_count = db.query(User).count()
        conversation_count = db.query(Conversation).count()
        message_count = db.query(Message).count()
        
        print(f"数据库统计:")
        print(f"  用户数量: {user_count}")
        print(f"  对话数量: {conversation_count}")
        print(f"  消息数量: {message_count}")
        
        # 如果有现有数据，为它们生成向量表示
        if conversation_count > 0:
            print("开始为现有对话生成向量表示...")
            from app.core.memory.vector_store import vector_store
            
            conversations = db.query(Conversation).all()
            for conv in conversations:
                try:
                    vector_store.update_conversation_vectors(db, conv.conversation_id, conv.user_id)
                    print(f"  已为对话 {conv.conversation_id} 生成向量表示")
                except Exception as e:
                    print(f"  警告: 为对话 {conv.conversation_id} 生成向量表示失败: {e}")
            
            print("向量表示生成完成！")
        
    except Exception as e:
        print(f"数据库测试失败: {e}")
    finally:
        db.close()

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