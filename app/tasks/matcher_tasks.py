"""匹配相关任务"""
from sqlalchemy import select
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.service import Service, ServiceType, ServiceStatus
from app.service_broker.service_manager import ServiceManager
from app.service_broker.matcher import ServiceMatcher
from app.service_broker.notification import MatchNotification
from app.utils.logger import get_logger

logger = get_logger()


@celery_app.task(name="app.tasks.matcher_tasks.match_service")
def match_service(service_id: str) -> dict:
    """为单个服务查找匹配"""
    try:
        logger.info(f"开始匹配服务: {service_id}")
        
        import asyncio
        
        async def _match():
            from sqlalchemy.ext.asyncio import AsyncSession
            from app.database import AsyncSessionLocal
            
            async with AsyncSessionLocal() as db:
                manager = ServiceManager()
                matcher = ServiceMatcher()
                notification = MatchNotification()
                
                # 获取服务
                service = await manager.get_service(db, service_id)
                if not service:
                    return {"error": "Service not found"}
                
                # 查找匹配
                matches = await matcher.find_matches(db, service, top_k=10)
                
                # 创建匹配记录
                if matches:
                    for match in matches[:5]:  # 只保存前5个
                        if service.type == ServiceType.SUPPLY:
                            await matcher.create_match_record(
                                db, service_id, match['service_id'], match['similarity_score']
                            )
                        else:
                            await matcher.create_match_record(
                                db, match['service_id'], service_id, match['similarity_score']
                            )
                
                # 通知用户
                from app.models.user import User
                stmt = select(User).where(User.id == service.user_id)
                result = await db.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    await notification.notify_matches(user.wecom_user_id, matches)
                
                return {
                    "service_id": service_id,
                    "matches_found": len(matches),
                    "notified": bool(user)
                }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_match())
        loop.close()
        
        logger.info(f"匹配完成: {service_id}")
        return result
        
    except Exception as e:
        logger.error(f"匹配服务失败: {e}")
        return {"error": str(e), "service_id": service_id}


@celery_app.task(name="app.tasks.matcher_tasks.batch_match_services")
def batch_match_services():
    """批量匹配活跃服务"""
    try:
        logger.info("开始批量匹配服务")
        
        import asyncio
        
        async def _batch_match():
            from sqlalchemy.ext.asyncio import AsyncSession
            from app.database import AsyncSessionLocal
            
            async with AsyncSessionLocal() as db:
                manager = ServiceManager()
                matcher = ServiceMatcher()
                
                # 获取所有活跃需求
                demands = await manager.get_active_services(db, "demand", limit=50)
                
                matched_count = 0
                for demand in demands:
                    matches = await matcher.find_matches(db, demand, top_k=5)
                    if matches:
                        matched_count += 1
                
                return {"processed": len(demands), "matched": matched_count}
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_batch_match())
        loop.close()
        
        logger.info(f"批量匹配完成: {result}")
        return result
        
    except Exception as e:
        logger.error(f"批量匹配失败: {e}")
        return {"error": str(e)}


@celery_app.task(name="app.tasks.matcher_tasks.clean_expired_services")
def clean_expired_services():
    """清理过期服务"""
    try:
        logger.info("开始清理过期服务")
        
        import asyncio
        
        async def _clean():
            from sqlalchemy.ext.asyncio import AsyncSession
            from app.database import AsyncSessionLocal
            
            async with AsyncSessionLocal() as db:
                manager = ServiceManager()
                count = await manager.clean_expired_services(db)
                return {"cleaned": count}
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_clean())
        loop.close()
        
        logger.info(f"清理完成: {result}")
        return result
        
    except Exception as e:
        logger.error(f"清理过期服务失败: {e}")
        return {"error": str(e)}

