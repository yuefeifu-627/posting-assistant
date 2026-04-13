"""数据库配置"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

settings = get_settings()

# 创建引擎
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # SQLite 需要这个参数
)

# 创建 SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建 Base
Base = declarative_base()


def get_db():
    """获取数据库会话的依赖函数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库"""
    from app.models import Theme, Post, UserPost, StyleProfile
    from app.models_user import User, UserSession, PasswordResetToken
    Base.metadata.create_all(bind=engine)