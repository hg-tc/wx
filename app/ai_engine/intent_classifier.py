"""意图分类器"""
from typing import Optional, Dict, Any
from app.ai_engine.deepseek_client import DeepSeekClient
from app.utils.logger import get_logger

logger = get_logger()


class IntentClassifier:
    """意图分类器"""
    
    # 意图类型
    SUPPLY_SERVICE = "supply_service"
    DEMAND_SERVICE = "demand_service"
    SHOPPING_COMPARE = "shopping_compare"
    QUERY_RECORDS = "query_records"
    CHITCHAT = "chitchat"
    HELP = "help"
    
    def __init__(self):
        self.client = DeepSeekClient()
        self.intent_prompt = """你是企业微信智能客服助手，负责识别用户意图。

用户消息：{user_message}

请判断用户意图，只返回以下之一（不要有其他任何解释）：
- supply_service: 用户想要提供/出售某种服务（如"我可以提供XX服务"、"我会XX"）
- demand_service: 用户需要购买某种服务（如"我需要XX服务"、"谁能帮我XX"）
- shopping_compare: 用户想购买商品并比价（如"帮我找XX"、"XX多少钱"、"帮我搜索XX"）
- query_records: 查询历史记录（如"查看我的记录"、"我的服务"）
- help: 询问如何使用或请求帮助（如"怎么用"、"帮助"）
- chitchat: 闲聊或其他（如问候、感谢等）

意图："""
    
    async def classify(self, user_message: str) -> Optional[str]:
        """分类用户意图"""
        try:
            prompt = self.intent_prompt.format(user_message=user_message)
            
            messages = [
                {"role": "system", "content": "你是一个意图分类助手，只返回意图类型，不要有任何其他内容。"},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.client.chat_completion(messages, temperature=0.3, max_tokens=50)
            
            if not response:
                return self.CHITCHAT
            
            # 清理响应，只保留意图类型
            intent = response.strip().lower()
            
            # 验证意图是否有效
            valid_intents = [
                self.SUPPLY_SERVICE,
                self.DEMAND_SERVICE,
                self.SHOPPING_COMPARE,
                self.QUERY_RECORDS,
                self.HELP,
                self.CHITCHAT
            ]
            
            for valid_intent in valid_intents:
                if valid_intent in intent:
                    logger.info(f"识别意图: {valid_intent}")
                    return valid_intent
            
            # 如果没有匹配到，默认为闲聊
            logger.warning(f"未识别的意图响应: {intent}，默认为chitchat")
            return self.CHITCHAT
            
        except Exception as e:
            logger.error(f"意图分类失败: {e}")
            return self.CHITCHAT
    
    async def is_service_supply(self, user_message: str) -> bool:
        """判断是否为服务供应"""
        intent = await self.classify(user_message)
        return intent == self.SUPPLY_SERVICE
    
    async def is_service_demand(self, user_message: str) -> bool:
        """判断是否为服务需求"""
        intent = await self.classify(user_message)
        return intent == self.DEMAND_SERVICE
    
    async def is_shopping(self, user_message: str) -> bool:
        """判断是否为购物比价"""
        intent = await self.classify(user_message)
        return intent == self.SHOPPING_COMPARE

