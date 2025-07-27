#!/usr/bin/env python3
"""
创建测试用户并验证认证功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy.orm import Session
from app.core.db.database import get_db, engine
from app.core.db.models import User
from app.core.db.crud import create_user, get_user_by_username
from app.core.security import verify_password, create_access_token, decode_access_token

def create_test_users():
    """创建测试用户"""
    db = next(get_db())
    
    try:
        # 检查是否已存在测试用户
        existing_user = get_user_by_username(db, "admin")
        if existing_user:
            print("✅ 管理员用户已存在")
        else:
            # 创建管理员用户
            admin_user = create_user(db, "admin", "admin123", is_admin=True)
            print(f"✅ 创建管理员用户: {admin_user.username} (ID: {admin_user.id})")
        
        # 检查普通用户
        existing_test_user = get_user_by_username(db, "testuser")
        if existing_test_user:
            print("✅ 测试用户已存在")
        else:
            # 创建普通用户
            test_user = create_user(db, "testuser", "testpass123", is_admin=False)
            print(f"✅ 创建测试用户: {test_user.username} (ID: {test_user.id})")
        
        return True
    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
        return False
    finally:
        db.close()

def test_authentication():
    """测试认证功能"""
    db = next(get_db())
    
    try:
        print("\n=== 测试认证功能 ===")
        
        # 测试用户查询
        user = get_user_by_username(db, "admin")
        if not user:
            print("❌ 找不到管理员用户")
            return False
        
        print(f"✅ 找到用户: {user.username}")
        print(f"   - ID: {user.id}")
        print(f"   - 是否管理员: {user.is_admin}")
        print(f"   - 密码哈希: {user.hashed_password[:20]}...")
        
        # 测试密码验证
        if verify_password("admin123", user.hashed_password):
            print("✅ 密码验证成功")
        else:
            print("❌ 密码验证失败")
            return False
        
        # 测试token创建和解码
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "is_admin": user.is_admin
        }
        token = create_access_token(token_data)
        print(f"✅ 创建token: {token[:30]}...")
        
        # 解码token
        decoded = decode_access_token(token)
        if decoded:
            print(f"✅ 解码token成功: {decoded}")
        else:
            print("❌ 解码token失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 认证测试失败: {e}")
        return False
    finally:
        db.close()

def list_all_users():
    """列出所有用户"""
    db = next(get_db())
    
    try:
        print("\n=== 数据库中的所有用户 ===")
        users = db.query(User).all()
        
        if not users:
            print("❌ 数据库中没有用户")
            return False
        
        for user in users:
            print(f"用户: {user.username}")
            print(f"  - ID: {user.id}")
            print(f"  - 邮箱: {user.email or 'N/A'}")
            print(f"  - 管理员: {user.is_admin}")
            print(f"  - 激活: {user.is_active}")
            print(f"  - 创建时间: {user.created_at}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 查询用户失败: {e}")
        return False
    finally:
        db.close()

def run_setup():
    """运行完整的设置流程"""
    print("=== 创建测试用户并验证认证功能 ===")
    
    # 创建测试用户
    if not create_test_users():
        return
    
    # 列出所有用户
    if not list_all_users():
        return
    
    # 测试认证功能
    if not test_authentication():
        return
    
    print("\n✅ 所有测试通过！现在可以使用以下账户登录：")
    print("管理员账户: admin / admin123")
    print("普通用户: testuser / testpass123")

# 为了兼容pytest，添加一个测试函数
def test_authentication_pytest():
    """pytest兼容的测试函数"""
    # 先运行设置
    run_setup()
    # 然后运行认证测试
    assert test_authentication()

if __name__ == "__main__":
    run_setup()