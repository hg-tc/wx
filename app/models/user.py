"""用户模型"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wecom_user_id = Column(String(128), unique=True, nullable=True, index=True, comment="企业微信用户ID（普通应用）")
    external_userid = Column(String(128), unique=True, nullable=True, index=True, comment="外部用户ID（客服应用）")
    nickname = Column(String(128), nullable=True, comment="昵称")
    avatar_url = Column(String(512), nullable=True, comment="头像URL")
    user_type = Column(String(32), nullable=False, default="internal", comment="用户类型: internal=内部员工, external=外部客户")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    
    # 关系
    services = relationship("Service", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, wecom_user_id={self.wecom_user_id}, nickname={self.nickname})>"

