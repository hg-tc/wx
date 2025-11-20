"""DeepSeek API客户端"""
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
from app.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger()


class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        self.model = settings.DEEPSEEK_MODEL
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Optional[str]:
        """聊天补全"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"DeepSeek回复: {content[:100]}...")
            return content
            
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            return None
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """获取文本向量"""
        try:
            # DeepSeek目前使用Chat API模拟embedding
            # 实际项目中可能需要使用专门的embedding模型
            # 这里使用一个简化的方法，实际使用时建议使用OpenAI的embedding API
            # 或其他专门的向量化服务
            
            # 临时方案：使用OpenAI的embedding（需要配置OpenAI API）
            from openai import AsyncOpenAI as OpenAIClient
            
            # 这里应该使用专门的embedding endpoint
            # 暂时返回None，需要集成实际的embedding服务
            logger.warning("需要配置专门的embedding服务")
            return None
            
        except Exception as e:
            logger.error(f"获取embedding失败: {e}")
            return None
    
    async def function_call(
        self, 
        messages: List[Dict[str, str]], 
        functions: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """函数调用"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=functions,
                function_call="auto"
            )
            
            message = response.choices[0].message
            
            if hasattr(message, 'function_call') and message.function_call:
                return {
                    "name": message.function_call.name,
                    "arguments": message.function_call.arguments
                }
            
            return None
            
        except Exception as e:
            logger.error(f"函数调用失败: {e}")
            return None

