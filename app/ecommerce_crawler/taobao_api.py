"""淘宝联盟API"""
import time
import hashlib
import hmac
import json
from typing import List, Dict, Any
import httpx
from app.ecommerce_crawler.base_crawler import BaseCrawler
from app.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger()


class TaobaoAPI(BaseCrawler):
    """淘宝联盟API"""
    
    def __init__(self):
        super().__init__()
        self.app_key = settings.TAOBAO_APP_KEY
        self.app_secret = settings.TAOBAO_APP_SECRET
        self.base_url = "https://eco.taobao.com/router/rest"
    
    def _sign(self, params: Dict[str, str]) -> str:
        """生成签名"""
        # 按字典序排序参数
        sorted_params = sorted(params.items())
        
        # 拼接参数字符串
        sign_str = self.app_secret
        for k, v in sorted_params:
            sign_str += f"{k}{v}"
        sign_str += self.app_secret
        
        # MD5签名
        return hashlib.md5(sign_str.encode()).hexdigest().upper()
    
    async def search(self, query: str, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        """搜索商品"""
        if not self.app_key or not self.app_secret:
            logger.warning("淘宝联盟API未配置，跳过")
            return []
        
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # 构建请求参数
            params = {
                "method": "taobao.tbk.dg.material.optional",
                "app_key": self.app_key,
                "timestamp": timestamp,
                "format": "json",
                "v": "2.0",
                "sign_method": "md5",
                "q": query,
                "page_no": str(page),
                "page_size": str(page_size),
            }
            
            # 生成签名
            params["sign"] = self._sign(params)
            
            # 发送请求
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.base_url, data=params)
                data = response.json()
                
                # 解析结果
                if "error_response" in data:
                    logger.error(f"淘宝API错误: {data['error_response']}")
                    return []
                
                result = data.get("tbk_dg_material_optional_response", {})
                item_list = result.get("result_list", {}).get("map_data", [])
                
                products = []
                for item in item_list:
                    product = self._parse_item(item)
                    if product:
                        products.append(product)
                
                logger.info(f"淘宝API搜索到{len(products)}个商品")
                return products
                
        except Exception as e:
            logger.error(f"淘宝API搜索失败: {e}")
            return []
    
    def _parse_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """解析商品数据"""
        try:
            price = float(item.get("zk_final_price", 0))
            coupon_amount = float(item.get("coupon_amount", 0))
            
            product = {
                "platform": "淘宝",
                "title": item.get("title", ""),
                "price": price,
                "original_price": float(item.get("reserve_price", price)),
                "coupon": coupon_amount,
                "final_price": price - coupon_amount,
                "url": item.get("coupon_share_url", item.get("url", "")),
                "image": item.get("pict_url", ""),
                "seller_rating": 0,  # 淘宝联盟API不提供评分
                "sales": int(item.get("volume", 0)),
                "shop_title": item.get("shop_title", ""),
            }
            
            return self.normalize_product(product, "淘宝")
            
        except Exception as e:
            logger.error(f"解析淘宝商品失败: {e}")
            return None

