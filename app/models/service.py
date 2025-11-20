"""服务供需模型"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Float, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.database import Base
import enum


class ServiceType(str, enum.Enum):
    """服务类型枚举"""
    SUPPLY = "supply"  # 供应
    DEMAND = "demand"  # 需求


class ServiceStatus(str, enum.Enum):
    """服务状态枚举"""
    ACTIVE = "active"  # 活跃
    MATCHED = "matched"  # 已匹配
    CLOSED = "closed"  # 已关闭


class MatchStatus(str, enum.Enum):
    """匹配状态枚举"""
    PENDING = "pending"  # 待确认
    ACCEPTED = "accepted"  # 已接受
    REJECTED = "rejected"  # 已拒绝


class Service(Base):
    """服务供需表"""
    __tablename__ = "services"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(ServiceType), nullable=False, index=True, comment="服务类型：供应/需求")
    category = Column(String(128), nullable=True, index=True, comment="服务分类")
    title = Column(String(256), nullable=False, comment="标题")
    description = Column(Text, nullable=False, comment="详细描述")
    price_range = Column(String(64), nullable=True, comment="价格区间")
    contact_info = Column(JSONB, nullable=True, comment="联系方式")
    embedding = Column(Vector(1536), nullable=True, comment="向量embeddings")
    status = Column(Enum(ServiceStatus), default=ServiceStatus.ACTIVE, nullable=False, index=True, comment="状态")
    tags = Column(ARRAY(Text), nullable=True, comment="标签数组")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True, comment="创建时间")
    expired_at = Column(DateTime, nullable=True, comment="过期时间")
    
    # 关系
    user = relationship("User", back_populates="services")
    supply_matches = relationship("Match", foreign_keys="Match.supply_id", back_populates="supply_service")
    demand_matches = relationship("Match", foreign_keys="Match.demand_id", back_populates="demand_service")
    
    def __repr__(self):
        return f"<Service(id={self.id}, type={self.type}, title={self.title})>"


class Match(Base):
    """匹配记录表"""
    __tablename__ = "matches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supply_id = Column(UUID(as_uuid=True), ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True, comment="供应服务ID")
    demand_id = Column(UUID(as_uuid=True), ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True, comment="需求服务ID")
    similarity_score = Column(Float, nullable=False, comment="相似度分数")
    status = Column(Enum(MatchStatus), default=MatchStatus.PENDING, nullable=False, index=True, comment="匹配状态")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    
    # 关系
    supply_service = relationship("Service", foreign_keys=[supply_id], back_populates="supply_matches")
    demand_service = relationship("Service", foreign_keys=[demand_id], back_populates="demand_matches")
    
    def __repr__(self):
        return f"<Match(id={self.id}, similarity_score={self.similarity_score}, status={self.status})>"

