"""价格比对器"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import ProductCache
from app.ecommerce_crawler.taobao_api import TaobaoAPI
from app.ecommerce_crawler.xianyu_crawler import XianyuCrawler
from app.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger()


class PriceComparator:
    """价格比对器"""
    
    def __init__(self):
        self.taobao_api = TaobaoAPI()
        self.xianyu_crawler = XianyuCrawler()
    
    async def search_all_platforms(
        self,
        db: AsyncSession,
        query: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """搜索所有平台"""
        # 检查缓存
        if use_cache:
            cached = await self._get_from_cache(db, query)
            if cached:
                logger.info(f"从缓存获取商品数据: {query}")
                return cached
        
        # 并发搜索多个平台
        results = []
        
        # 淘宝
        taobao_products = await self.taobao_api.search(query)
        results.extend(taobao_products)
        
        # 咸鱼（可选，因为爬虫可能不稳定）
        try:
            xianyu_products = await self.xianyu_crawler.search(query)
            results.extend(xianyu_products)
        except Exception as e:
            logger.warning(f"咸鱼搜索失败: {e}")
        
        # 微信小商店（需要API接入）
        # wechat_products = await self.wechat_shop.search(query)
        # results.extend(wechat_products)
        
        # 去重和排序
        deduplicated = self._deduplicate_products(results)
        sorted_products = self._sort_by_price(deduplicated)
        
        # 找出最优惠的
        best_deal = self._find_best_deal(sorted_products)
        
        result = {
            "query": query,
            "total_count": len(sorted_products),
            "results": sorted_products[:20],  # 最多返回20个
            "best_deal": best_deal,
            "platforms": list(set(p['platform'] for p in sorted_products)),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # 缓存结果
        await self._save_to_cache(db, query, sorted_products)
        
        logger.info(f"搜索完成: {query}, 共{len(sorted_products)}个商品")
        return result
    
    def _deduplicate_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重商品"""
        seen = set()
        unique_products = []
        
        for product in products:
            # 使用标题的前50个字符作为去重key
            key = product['title'][:50].lower()
            if key not in seen:
                seen.add(key)
                unique_products.append(product)
        
        return unique_products
    
    def _sort_by_price(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按价格排序"""
        return sorted(products, key=lambda x: x.get('final_price', float('inf')))
    
    def _find_best_deal(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """找出最优惠的商品"""
        if not products:
            return {}
        
        # 综合考虑价格、评分、销量
        def score(p):
            price = p.get('final_price', float('inf'))
            rating = p.get('seller_rating', 0)
            sales = p.get('sales', 0)
            
            # 价格权重最高
            price_score = 1 / (price + 1) * 100
            rating_score = rating * 2
            sales_score = min(sales / 1000, 10)  # 销量最高10分
            
            return price_score + rating_score + sales_score
        
        return max(products, key=score)
    
    async def _get_from_cache(
        self,
        db: AsyncSession,
        query: str
    ) -> Dict[str, Any]:
        """从缓存获取"""
        try:
            stmt = select(ProductCache).where(
                ProductCache.search_query == query,
                ProductCache.expires_at > datetime.utcnow()
            )
            
            result = await db.execute(stmt)
            cached_products = result.scalars().all()
            
            if not cached_products:
                return None
            
            # 按平台分组
            products = []
            for cache in cached_products:
                product_data = cache.product_data
                product_data['platform'] = cache.platform
                product_data['price'] = float(cache.price) if cache.price else 0
                products.append(product_data)
            
            best_deal = self._find_best_deal(products)
            
            return {
                "query": query,
                "total_count": len(products),
                "results": products,
                "best_deal": best_deal,
                "platforms": list(set(p['platform'] for p in products)),
                "updated_at": cached_products[0].cached_at.isoformat(),
                "from_cache": True
            }
            
        except Exception as e:
            logger.error(f"从缓存获取失败: {e}")
            return None
    
    async def _save_to_cache(
        self,
        db: AsyncSession,
        query: str,
        products: List[Dict[str, Any]]
    ) -> bool:
        """保存到缓存"""
        try:
            # 删除旧缓存
            stmt = select(ProductCache).where(ProductCache.search_query == query)
            result = await db.execute(stmt)
            old_caches = result.scalars().all()
            for old_cache in old_caches:
                await db.delete(old_cache)
            
            # 保存新缓存
            expires_at = datetime.utcnow() + timedelta(seconds=settings.PRODUCT_CACHE_EXPIRE)
            
            for product in products[:50]:  # 最多缓存50个
                cache = ProductCache(
                    search_query=query,
                    platform=product['platform'],
                    product_data=product,
                    price=product.get('final_price', 0),
                    url=product.get('url', ''),
                    expires_at=expires_at
                )
                db.add(cache)
            
            await db.commit()
            logger.info(f"缓存商品数据: {query}, {len(products)}个")
            return True
            
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
            await db.rollback()
            return False

