from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.getenv('DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'chemagent.db')}")
print('Using database:', DATABASE_URL)

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