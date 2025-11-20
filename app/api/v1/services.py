"""服务管理API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.service_broker.service_manager import ServiceManager
from app.service_broker.matcher import ServiceMatcher
from app.utils.logger import get_logger

logger = get_logger()
router = APIRouter()


class ServiceCreate(BaseModel):
    """服务创建请求"""
    user_id: str
    service_type: str
    title: str
    description: str
    category: str = ""
    price_range: str = ""
    tags: List[str] = []


class MatchUpdate(BaseModel):
    """匹配状态更新"""
    status: str


@router.post("/supply")
async def create_supply_service(
    service: ServiceCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建供应服务"""
    try:
        manager = ServiceManager()
        entities = {
            "title": service.title,
            "description": service.description,
            "category": service.category,
            "price_range": service.price_range,
            "tags": service.tags
        }
        
        result = await manager.create_service(db, service.user_id, "supply", entities)
        
        if result:
            return {"success": True, "service_id": str(result.id)}
        else:
            raise HTTPException(status_code=500, detail="创建服务失败")
    
    except Exception as e:
        logger.error(f"创建供应服务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/demand")
async def create_demand_service(
    service: ServiceCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建需求服务"""
    try:
        manager = ServiceManager()
        entities = {
            "title": service.title,
            "description": service.description,
            "category": service.category,
            "price_range": service.price_range,
            "tags": service.tags
        }
        
        result = await manager.create_service(db, service.user_id, "demand", entities)
        
        if result:
            return {"success": True, "service_id": str(result.id)}
        else:
            raise HTTPException(status_code=500, detail="创建服务失败")
    
    except Exception as e:
        logger.error(f"创建需求服务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/matches/{service_id}")
async def get_matches(
    service_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取服务的匹配结果"""
    try:
        manager = ServiceManager()
        matcher = ServiceMatcher()
        
        service = await manager.get_service(db, service_id)
        if not service:
            raise HTTPException(status_code=404, detail="服务不存在")
        
        matches = await matcher.find_matches(db, service)
        
        return {
            "service_id": service_id,
            "matches": matches
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取匹配结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/matches/{match_id}")
async def update_match_status(
    match_id: str,
    update: MatchUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新匹配状态"""
    try:
        matcher = ServiceMatcher()
        success = await matcher.update_match_status(db, match_id, update.status)
        
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="匹配记录不存在")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新匹配状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

