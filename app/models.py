from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Theme(Base):
    """主题模型 - 每个主题可以有多篇帖子"""
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    post_length = Column(Integer, default=500)  # 发帖字数限制
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联帖子
    posts = relationship("Post", back_populates="theme", cascade="all, delete-orphan")


class Post(Base):
    """帖子模型 - 属于某个主题"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    theme_id = Column(Integer, ForeignKey("themes.id"), nullable=False)
    summary = Column(Text, nullable=True)  # 用户提供的提要
    requirements = Column(Text, nullable=True)  # 主办方任务要求
    content = Column(Text, nullable=False)  # 生成的帖子内容
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联主题
    theme = relationship("Theme", back_populates="posts")


class UserPost(Base):
    """用户语料库 - 存储用户的历史帖子，用于学习写作风格"""
    __tablename__ = "user_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    tags = Column(String(255), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StyleProfile(Base):
    """风格特征 - 存储AI分析后的写作风格特征"""
    __tablename__ = "style_profile"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)  # 风格特征描述
    post_count = Column(Integer, default=0)  # 分析时使用的帖子数量
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)