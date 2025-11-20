"""对话历史模型"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class MessageRole(str, enum.Enum):
    """消息角色枚举"""
    USER = "user"  # 用户
    ASSISTANT = "assistant"  # 助手


class Conversation(Base):
    """对话历史表"""
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(128), nullable=False, index=True, comment="会话ID")
    role = Column(Enum(MessageRole), nullable=False, comment="角色：用户/助手")
    content = Column(Text, nullable=False, comment="消息内容")
    intent = Column(String(64), nullable=True, comment="识别的意图")
    entities = Column(JSONB, nullable=True, comment="提取的实体")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True, comment="创建时间")
    
    # 关系
    user = relationship("User", back_populates="conversations")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, role={self.role}, session_id={self.session_id})>"

