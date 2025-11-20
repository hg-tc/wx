"""企业微信API客户端"""
import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger()


class WeComClient:
    """企业微信API客户端"""
    
    def __init__(self):
        self.corp_id = settings.WECOM_CORP_ID
        self.agent_id = settings.WECOM_AGENT_ID
        self.secret = settings.WECOM_SECRET
        self.base_url = "https://qyapi.weixin.qq.com/cgi-bin"
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        
    async def get_access_token(self, force_refresh: bool = False) -> str:
        """获取access_token"""
        # 如果token未过期且不强制刷新，直接返回
        if (not force_refresh and 
            self._access_token and 
            self._token_expires_at and 
            datetime.now() < self._token_expires_at):
            return self._access_token
        
        # 请求新token
        url = f"{self.base_url}/gettoken"
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.secret,
            "debug": 1  # 添加debug参数以支持hint值查询
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
            
            if data.get("errcode") != 0:
                logger.error(f"获取access_token失败: {data}")
                raise Exception(f"获取access_token失败: {data.get('errmsg')}")
            
            self._access_token = data["access_token"]
            expires_in = data.get("expires_in", 7200)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # 提前5分钟过期
            
            logger.info(f"成功获取access_token，将于 {self._token_expires_at} 过期")
            return self._access_token
    
    async def send_text_message(self, user_id: str, content: str) -> Dict[str, Any]:
        """发送文本消息"""
        token = await self.get_access_token()
        url = f"{self.base_url}/message/send"
        
        data = {
            "touser": user_id,
            "msgtype": "text",
            "agentid": self.agent_id,
            "text": {
                "content": content
            },
            "safe": 0
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                params={"access_token": token, "debug": 1},
                json=data
            )
            result = response.json()
            
            if result.get("errcode") != 0:
                logger.error(f"发送消息失败: {result}")
            else:
                logger.info(f"成功发送消息给用户 {user_id}")
            
            return result
    
    async def send_markdown_message(self, user_id: str, content: str) -> Dict[str, Any]:
        """发送markdown消息"""
        token = await self.get_access_token()
        url = f"{self.base_url}/message/send"
        
        data = {
            "touser": user_id,
            "msgtype": "markdown",
            "agentid": self.agent_id,
            "markdown": {
                "content": content
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                params={"access_token": token, "debug": 1},
                json=data
            )
            result = response.json()
            
            if result.get("errcode") != 0:
                logger.error(f"发送markdown消息失败: {result}")
            else:
                logger.info(f"成功发送markdown消息给用户 {user_id}")
            
            return result
    
    async def send_news_message(self, user_id: str, articles: list) -> Dict[str, Any]:
        """发送图文消息"""
        token = await self.get_access_token()
        url = f"{self.base_url}/message/send"
        
        data = {
            "touser": user_id,
            "msgtype": "news",
            "agentid": self.agent_id,
            "news": {
                "articles": articles
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                params={"access_token": token, "debug": 1},
                json=data
            )
            result = response.json()
            
            if result.get("errcode") != 0:
                logger.error(f"发送图文消息失败: {result}")
            else:
                logger.info(f"成功发送图文消息给用户 {user_id}")
            
            return result
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """获取用户信息"""
        token = await self.get_access_token()
        url = f"{self.base_url}/user/get"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params={"access_token": token, "userid": user_id, "debug": 1}
            )
            result = response.json()
            
            if result.get("errcode") != 0:
                logger.error(f"获取用户信息失败: {result}")
            
            return result

