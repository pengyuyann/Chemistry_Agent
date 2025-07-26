#!/usr/bin/env python3
"""
查看向量数据库内容的脚本
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.db.database import DATABASE_URL
from app.core.db.models import User, Conversation, Message, ConversationVector

def view_vector_database():
    """查看向量数据库的内容"""
    print("🔍 向量数据库内容查看器")
    print("=" * 50)
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 1. 基本统计信息
        print("\n📊 数据库统计信息:")
        user_count = db.query(User).count()
        conversation_count = db.query(Conversation).count()
        message_count = db.query(Message).count()
        vector_count = db.query(ConversationVector).count()
        
        print(f"  👥 用户数量: {user_count}")
        print(f"  💬 对话数量: {conversation_count}")
        print(f"  📝 消息数量: {message_count}")
        print(f"  🔢 向量记录数量: {vector_count}")
        
        # 2. 查看用户信息
        print("\n👥 用户列表:")
        users = db.query(User).all()
        for user in users:
            print(f"  ID: {user.id}, 用户名: {user.username}, 管理员: {user.is_admin}")
            print(f"      API调用次数: {user.api_calls_count}, 今日调用: {user.api_calls_today}")
            print(f"      最后登录: {user.last_login}")
        
        # 3. 查看对话信息
        print("\n💬 对话列表 (最近10条):")
        conversations = db.query(Conversation).order_by(Conversation.created_at.desc()).limit(10).all()
        for conv in conversations:
            print(f"  对话ID: {conv.conversation_id}")
            print(f"    标题: {conv.title}")
            print(f"    用户ID: {conv.user_id}")
            print(f"    模型: {conv.model_used}")
            print(f"    创建时间: {conv.created_at}")
            
            # 查看该对话的消息数量
            msg_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
            print(f"    消息数量: {msg_count}")
            print()
        
        # 4. 查看向量存储信息
        print("\n🔢 向量存储详情:")
        vectors = db.query(ConversationVector).all()
        if vectors:
            for vec in vectors:
                print(f"  对话ID: {vec.conversation_id}")
                print(f"    用户ID: {vec.user_id}")
                
                # 解析关键实体
                if vec.key_entities:
                    try:
                        entities = json.loads(vec.key_entities)
                        print(f"    关键实体: {entities}")
                    except:
                        print(f"    关键实体: {vec.key_entities}")
                
                # 解析话题
                if vec.topics:
                    try:
                        topics = json.loads(vec.topics)
                        print(f"    话题: {topics}")
                    except:
                        print(f"    话题: {vec.topics}")
                
                # 检查向量维度
                if vec.summary_embedding:
                    try:
                        embedding = json.loads(vec.summary_embedding)
                        print(f"    向量维度: {len(embedding)}")
                        print(f"    向量前5个值: {embedding[:5]}")
                    except:
                        print(f"    向量数据: 解析失败")
                
                print(f"    创建时间: {vec.created_at}")
                print(f"    更新时间: {vec.updated_at}")
                print()
        else:
            print("  暂无向量数据")
        
        # 5. 查看消息的向量信息
        print("\n📝 消息向量信息 (最近5条有向量的消息):")
        messages_with_vectors = db.query(Message).filter(Message.embedding.isnot(None)).limit(5).all()
        if messages_with_vectors:
            for msg in messages_with_vectors:
                print(f"  消息ID: {msg.id}")
                print(f"    角色: {msg.role}")
                print(f"    内容预览: {msg.content[:100]}...")
                print(f"    向量ID: {msg.vector_id}")
                print(f"    嵌入模型: {msg.embedding_model}")
                
                if msg.embedding:
                    try:
                        embedding = json.loads(msg.embedding)
                        print(f"    向量维度: {len(embedding)}")
                    except:
                        print(f"    向量数据: 解析失败")
                print()
        else:
            print("  暂无消息向量数据")
        
        # 6. 数据库健康检查
        print("\n🏥 数据库健康检查:")
        
        # 检查有多少消息有向量
        messages_with_embedding = db.query(Message).filter(Message.embedding.isnot(None)).count()
        print(f"  有向量的消息: {messages_with_embedding}/{message_count}")
        
        # 检查向量数据完整性
        incomplete_vectors = db.query(ConversationVector).filter(
            ConversationVector.summary_embedding.is_(None)
        ).count()
        print(f"  不完整的向量记录: {incomplete_vectors}/{vector_count}")
        
        # 检查最近的活动
        recent_messages = db.query(Message).filter(
            Message.created_at >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        print(f"  今日新消息: {recent_messages}")
        
    except Exception as e:
        print(f"❌ 查看数据库时出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    view_vector_database()