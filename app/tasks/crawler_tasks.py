"""爬虫相关任务"""
from datetime import datetime
from sqlalchemy import select
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.product import ProductCache
from app.ecommerce_crawler.price_comparator import PriceComparator
from app.utils.logger import get_logger

logger = get_logger()


@celery_app.task(name="app.tasks.crawler_tasks.crawl_products")
def crawl_products(query: str, user_id: str) -> dict:
    """异步爬取商品"""
    try:
        logger.info(f"开始爬取商品: {query}")
        
        # 注意：这里使用同步方式，因为Celery worker中
        # 实际生产环境建议使用 celery 的异步支持或运行异步事件循环
        import asyncio
        
        async def _crawl():
            from sqlalchemy.ext.asyncio import AsyncSession
            from app.database import AsyncSessionLocal
            
            async with AsyncSessionLocal() as db:
                comparator = PriceComparator()
                result = await comparator.search_all_platforms(db, query, use_cache=False)
                return result
        
        # 运行异步任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_crawl())
        loop.close()
        
        logger.info(f"爬取完成: {query}, 共{result.get('total_count', 0)}个商品")
        return result
        
    except Exception as e:
        logger.error(f"爬取商品失败: {e}")
        return {"error": str(e), "query": query}


@celery_app.task(name="app.tasks.crawler_tasks.clean_expired_cache")
def clean_expired_cache():
    """清理过期缓存"""
    try:
        db = SessionLocal()
        
        # 删除过期缓存
        stmt = select(ProductCache).where(ProductCache.expires_at < datetime.utcnow())
        result = db.execute(stmt)
        expired_caches = result.scalars().all()
        
        count = 0
        for cache in expired_caches:
            db.delete(cache)
            count += 1
        
        db.commit()
        db.close()
        
        logger.info(f"清理过期缓存: {count}条")
        return {"cleaned": count}
        
    except Exception as e:
        logger.error(f"清理缓存失败: {e}")
        return {"error": str(e)}

