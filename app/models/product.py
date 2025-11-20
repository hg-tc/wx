"""商品缓存模型"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class ProductCache(Base):
    """商品缓存表"""
    __tablename__ = "product_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    search_query = Column(String(256), nullable=False, index=True, comment="搜索关键词")
    platform = Column(String(32), nullable=False, index=True, comment="平台名称")
    product_data = Column(JSONB, nullable=False, comment="商品详情JSON")
    price = Column(DECIMAL(10, 2), nullable=True, comment="价格")
    url = Column(Text, nullable=False, comment="商品链接")
    cached_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="缓存时间")
    expires_at = Column(DateTime, nullable=False, index=True, comment="过期时间")
    
    def __repr__(self):
        return f"<ProductCache(id={self.id}, platform={self.platform}, search_query={self.search_query})>"

