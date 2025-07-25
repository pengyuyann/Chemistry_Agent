from app.core.db.database import engine
from app.core.db.models import Base, User, Conversation, Message
from app.core.db.crud import create_user
from sqlalchemy.orm import Session
import os

def init_db():
    print("[DB] 正在创建所有表...")
    Base.metadata.create_all(bind=engine)
    print("[DB] 数据库表创建完成。")
    # 可选：创建初始管理员账号
    admin_username = os.getenv("INIT_ADMIN_USERNAME", "admin")
    admin_password = os.getenv("INIT_ADMIN_PASSWORD", "admin123")
    with Session(engine) as db:
        if not db.query(User).filter(User.username == admin_username).first():
            create_user(db, admin_username, admin_password, is_admin=True)
            print(f"[DB] 已创建初始管理员账号: {admin_username} / {admin_password}")
        else:
            print(f"[DB] 管理员账号 {admin_username} 已存在，无需重复创建。")

if __name__ == "__main__":
    init_db() 