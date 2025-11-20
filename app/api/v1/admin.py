"""管理后台API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.service import Service, Match
from app.models.user import User
from app.models.conversation import Conversation
from app.service_broker.service_manager import ServiceManager
from app.utils.logger import get_logger

logger = get_logger()
router = APIRouter()


@router.get("/services")
async def list_services(
    db: AsyncSession = Depends(get_db),
    service_type: str = Query(None),
    status: str = Query(None),
    limit: int = Query(50, le=100)
):
    """获取服务列表"""
    try:
        stmt = select(Service)
        
        if service_type:
            stmt = stmt.where(Service.type == service_type)
        if status:
            stmt = stmt.where(Service.status == status)
        
        stmt = stmt.order_by(Service.created_at.desc()).limit(limit)
        
        result = await db.execute(stmt)
        services = result.scalars().all()
        
        return {
            "total": len(services),
            "services": [
                {
                    "id": str(s.id),
                    "user_id": str(s.user_id),
                    "type": s.type.value,
                    "title": s.title,
                    "category": s.category,
                    "status": s.status.value,
                    "created_at": s.created_at.isoformat() if s.created_at else None
                }
                for s in services
            ]
        }
    
    except Exception as e:
        logger.error(f"获取服务列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_analytics(db: AsyncSession = Depends(get_db)):
    """获取统计数据"""
    try:
        # 统计用户数
        user_count = await db.scalar(select(func.count(User.id)))
        
        # 统计服务数
        service_count = await db.scalar(select(func.count(Service.id)))
        supply_count = await db.scalar(
            select(func.count(Service.id)).where(Service.type == "supply")
        )
        demand_count = await db.scalar(
            select(func.count(Service.id)).where(Service.type == "demand")
        )
        
        # 统计匹配数
        match_count = await db.scalar(select(func.count(Match.id)))
        matched_count = await db.scalar(
            select(func.count(Match.id)).where(Match.status == "accepted")
        )
        
        # 统计对话数
        conversation_count = await db.scalar(select(func.count(Conversation.id)))
        
        return {
            "users": user_count or 0,
            "services": {
                "total": service_count or 0,
                "supply": supply_count or 0,
                "demand": demand_count or 0
            },
            "matches": {
                "total": match_count or 0,
                "accepted": matched_count or 0
            },
            "conversations": conversation_count or 0
        }
    
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/services/{service_id}")
async def delete_service(
    service_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除服务"""
    try:
        manager = ServiceManager()
        success = await manager.delete_service(db, service_id)
        
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="服务不存在")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除服务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

