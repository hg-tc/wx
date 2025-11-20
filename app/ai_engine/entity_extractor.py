"""实体提取器"""
import json
from typing import Dict, Any, Optional
from app.ai_engine.deepseek_client import DeepSeekClient
from app.utils.logger import get_logger

logger = get_logger()


class EntityExtractor:
    """实体提取器"""
    
    def __init__(self):
        self.client = DeepSeekClient()
    
    async def extract_service_entities(self, user_message: str, intent: str) -> Dict[str, Any]:
        """提取服务相关实体"""
        service_type = "供应" if intent == "supply_service" else "需求"
        
        prompt = f"""从用户消息中提取服务相关信息，返回JSON格式。

用户消息：{user_message}
服务类型：{service_type}

请提取以下信息（如果没有提到则留空）：
- title: 服务标题（简短概括，10字以内）
- description: 详细描述
- category: 服务分类（如：技术开发、设计、咨询、维修等）
- price_range: 价格区间（如：100-500元、面议等）
- tags: 相关标签（数组，如：["Python", "后端开发"]）

只返回JSON，不要有其他内容："""
        
        try:
            messages = [
                {"role": "system", "content": "你是一个信息提取助手，只返回JSON格式的结果。"},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.client.chat_completion(messages, temperature=0.3, max_tokens=500)
            
            if not response:
                return self._default_service_entities(user_message)
            
            # 提取JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            entities = json.loads(response)
            
            # 验证必要字段
            if not entities.get('title'):
                entities['title'] = user_message[:50]
            if not entities.get('description'):
                entities['description'] = user_message
            
            logger.info(f"提取的实体: {entities}")
            return entities
            
        except Exception as e:
            logger.error(f"实体提取失败: {e}")
            return self._default_service_entities(user_message)
    
    async def extract_shopping_entities(self, user_message: str) -> Dict[str, Any]:
        """提取购物相关实体"""
        prompt = f"""从用户消息中提取商品搜索关键词和偏好，返回JSON格式。

用户消息：{user_message}

请提取以下信息：
- query: 搜索关键词（核心商品名称）
- category: 商品分类（如：电子产品、服装、食品等）
- price_range: 价格范围（如果提到，格式：min-max）
- preferences: 用户偏好（数组，如：["全新"、"包邮"、"品牌"]）

只返回JSON，不要有其他内容："""
        
        try:
            messages = [
                {"role": "system", "content": "你是一个信息提取助手，只返回JSON格式的结果。"},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.client.chat_completion(messages, temperature=0.3, max_tokens=300)
            
            if not response:
                return {"query": user_message, "category": "", "price_range": "", "preferences": []}
            
            # 提取JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            entities = json.loads(response)
            
            # 验证必要字段
            if not entities.get('query'):
                entities['query'] = user_message
            
            logger.info(f"提取的购物实体: {entities}")
            return entities
            
        except Exception as e:
            logger.error(f"购物实体提取失败: {e}")
            return {"query": user_message, "category": "", "price_range": "", "preferences": []}
    
    def _default_service_entities(self, user_message: str) -> Dict[str, Any]:
        """默认服务实体"""
        return {
            "title": user_message[:50],
            "description": user_message,
            "category": "",
            "price_range": "面议",
            "tags": []
        }

