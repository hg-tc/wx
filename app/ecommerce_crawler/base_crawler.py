"""爬虫基类"""
import random
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from app.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger()


class BaseCrawler(ABC):
    """爬虫基类"""
    
    def __init__(self):
        self.timeout = settings.CRAWLER_TIMEOUT
        self.max_concurrent = settings.CRAWLER_MAX_CONCURRENT
        self.proxy_pool = settings.CRAWLER_PROXY_POOL
        self.user_agents = [
            settings.CRAWLER_USER_AGENT,
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
    
    def get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        return random.choice(self.user_agents)
    
    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "User-Agent": self.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    
    def get_proxy(self) -> Optional[str]:
        """获取代理"""
        if self.proxy_pool:
            # 这里应该实现代理池逻辑
            # 可以从代理服务获取可用代理
            pass
        return None
    
    @abstractmethod
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """搜索商品（子类实现）"""
        pass
    
    def normalize_product(self, raw_product: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """标准化商品数据"""
        return {
            "platform": platform,
            "title": raw_product.get("title", ""),
            "price": self._parse_price(raw_product.get("price", 0)),
            "original_price": self._parse_price(raw_product.get("original_price", 0)),
            "coupon": self._parse_price(raw_product.get("coupon", 0)),
            "final_price": self._calculate_final_price(raw_product),
            "url": raw_product.get("url", ""),
            "image": raw_product.get("image", ""),
            "seller_rating": raw_product.get("seller_rating", 0),
            "sales": raw_product.get("sales", 0),
            "location": raw_product.get("location", ""),
        }
    
    def _parse_price(self, price: Any) -> float:
        """解析价格"""
        if isinstance(price, (int, float)):
            return float(price)
        
        if isinstance(price, str):
            # 移除非数字字符
            price_str = ''.join(c for c in price if c.isdigit() or c == '.')
            try:
                return float(price_str)
            except ValueError:
                return 0.0
        
        return 0.0
    
    def _calculate_final_price(self, product: Dict[str, Any]) -> float:
        """计算最终价格"""
        price = self._parse_price(product.get("price", 0))
        coupon = self._parse_price(product.get("coupon", 0))
        return max(0, price - coupon)

