"""服务管理器"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.service import Service, ServiceType, ServiceStatus
from app.models.user import User
from app.ai_engine.embedding_service import EmbeddingService
from app.utils.logger import get_logger

logger = get_logger()


class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
    
    async def create_service(
        self,
        db: AsyncSession,
        user_id: str,
        service_type: str,
        entities: Dict[str, Any],
        expire_days: int = 30
    ) -> Optional[Service]:
        """创建服务"""
        try:
            # 获取向量
            description = entities.get('description', '')
            embedding = await self.embedding_service.get_embedding(description)
            
            # 创建服务
            service = Service(
                user_id=user_id,
                type=ServiceType(service_type),
                category=entities.get('category', ''),
                title=entities.get('title', ''),
                description=description,
                price_range=entities.get('price_range', ''),
                contact_info=entities.get('contact_info', {}),
                embedding=embedding,
                tags=entities.get('tags', []),
                status=ServiceStatus.ACTIVE,
                expired_at=datetime.utcnow() + timedelta(days=expire_days)
            )
            
            db.add(service)
            await db.commit()
            await db.refresh(service)
            
            logger.info(f"创建服务成功: {service.id}, type={service_type}, title={service.title}")
            return service
            
        except Exception as e:
            logger.error(f"创建服务失败: {e}")
            await db.rollback()
            return None
    
    async def get_service(self, db: AsyncSession, service_id: str) -> Optional[Service]:
        """获取服务"""
        try:
            stmt = select(Service).where(Service.id == service_id)
            result = await db.execute(stmt)
            service = result.scalar_one_or_none()
            return service
        except Exception as e:
            logger.error(f"获取服务失败: {e}")
            return None
    
    async def get_user_services(
        self,
        db: AsyncSession,
        user_id: str,
        service_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[Service]:
        """获取用户的服务列表"""
        try:
            stmt = select(Service).where(Service.user_id == user_id)
            
            if service_type:
                stmt = stmt.where(Service.type == ServiceType(service_type))
            
            if status:
                stmt = stmt.where(Service.status == ServiceStatus(status))
            
            stmt = stmt.order_by(Service.created_at.desc()).limit(limit)
            
            result = await db.execute(stmt)
            services = result.scalars().all()
            return list(services)
            
        except Exception as e:
            logger.error(f"获取用户服务列表失败: {e}")
            return []
    
    async def get_active_services(
        self,
        db: AsyncSession,
        service_type: str,
        limit: int = 100
    ) -> List[Service]:
        """获取活跃服务"""
        try:
            stmt = select(Service).where(
                Service.type == ServiceType(service_type),
                Service.status == ServiceStatus.ACTIVE,
                Service.expired_at > datetime.utcnow()
            ).order_by(Service.created_at.desc()).limit(limit)
            
            result = await db.execute(stmt)
            services = result.scalars().all()
            return list(services)
            
        except Exception as e:
            logger.error(f"获取活跃服务失败: {e}")
            return []
    
    async def update_service_status(
        self,
        db: AsyncSession,
        service_id: str,
        status: str
    ) -> bool:
        """更新服务状态"""
        try:
            service = await self.get_service(db, service_id)
            if not service:
                return False
            
            service.status = ServiceStatus(status)
            await db.commit()
            
            logger.info(f"更新服务状态: {service_id} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"更新服务状态失败: {e}")
            await db.rollback()
            return False
    
    async def delete_service(self, db: AsyncSession, service_id: str) -> bool:
        """删除服务"""
        try:
            service = await self.get_service(db, service_id)
            if not service:
                return False
            
            await db.delete(service)
            await db.commit()
            
            logger.info(f"删除服务: {service_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除服务失败: {e}")
            await db.rollback()
            return False
    
    async def clean_expired_services(self, db: AsyncSession) -> int:
        """清理过期服务"""
        try:
            stmt = select(Service).where(
                Service.expired_at < datetime.utcnow(),
                Service.status == ServiceStatus.ACTIVE
            )
            
            result = await db.execute(stmt)
            expired_services = result.scalars().all()
            
            count = 0
            for service in expired_services:
                service.status = ServiceStatus.CLOSED
                count += 1
            
            await db.commit()
            logger.info(f"清理过期服务: {count}个")
            return count
            
        except Exception as e:
            logger.error(f"清理过期服务失败: {e}")
            await db.rollback()
            return 0

