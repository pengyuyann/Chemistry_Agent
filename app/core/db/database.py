from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
import os

# 获取项目根目录下的 app 文件夹路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_DIR = os.path.join(PROJECT_ROOT, 'app')

# 确保 app 目录存在
os.makedirs(APP_DIR, exist_ok=True)

# 使用绝对路径构建数据库 URL
DB_PATH = os.path.abspath(os.path.join(APP_DIR, 'chemagent.db'))
DATABASE_URL = os.getenv('DATABASE_URL', f"sqlite:///{DB_PATH}")

print(f'Using database: {DATABASE_URL}')
print(f'Database file path: {DB_PATH}')
print(f'Database file exists: {os.path.exists(DB_PATH)}')

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()