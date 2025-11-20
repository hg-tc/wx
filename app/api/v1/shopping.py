"""购物比价API"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.ecommerce_crawler.price_comparator import PriceComparator
from app.tasks.crawler_tasks import crawl_products
from app.utils.logger import get_logger

logger = get_logger()
router = APIRouter()


class SearchRequest(BaseModel):
    """搜索请求"""
    query: str
    user_id: str = ""
    use_cache: bool = True


@router.post("/search")
async def search_products(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """搜索商品（同步返回）"""
    try:
        comparator = PriceComparator()
        result = await comparator.search_all_platforms(db, request.query, request.use_cache)
        
        return result
    
    except Exception as e:
        logger.error(f"搜索商品失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/async")
async def search_products_async(
    request: SearchRequest,
    background_tasks: BackgroundTasks
):
    """搜索商品（异步任务）"""
    try:
        task = crawl_products.delay(request.query, request.user_id)
        
        return {
            "task_id": task.id,
            "status": "pending",
            "message": "搜索任务已提交"
        }
    
    except Exception as e:
        logger.error(f"提交搜索任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{task_id}")
async def get_task_result(task_id: str):
    """获取任务结果"""
    try:
        from celery.result import AsyncResult
        from app.tasks.celery_app import celery_app
        
        task = AsyncResult(task_id, app=celery_app)
        
        if task.ready():
            return {
                "task_id": task_id,
                "status": "completed",
                "result": task.result
            }
        elif task.failed():
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(task.info)
            }
        else:
            return {
                "task_id": task_id,
                "status": "pending",
                "message": "任务处理中"
            }
    
    except Exception as e:
        logger.error(f"获取任务结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

