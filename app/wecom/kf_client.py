"""企业微信客服API客户端"""
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger()


class KfClient:
    """企业微信客服API客户端"""
    
    def __init__(self):
        self.corp_id = settings.WECOM_CORP_ID
        self.kf_secret = settings.WECOM_KF_SECRET or settings.WECOM_SECRET
        self.kf_account_id = settings.WECOM_KF_ACCOUNT_ID
        self.base_url = "https://qyapi.weixin.qq.com/cgi-bin"
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
    
    async def get_access_token(self, force_refresh: bool = False) -> str:
        """获取客服专用access_token"""
        # 如果token未过期且不强制刷新，直接返回
        if (not force_refresh and 
            self._access_token and 
            self._token_expires_at and 
            datetime.now() < self._token_expires_at):
            return self._access_token
        
        # 请求新token
        url = f"{self.base_url}/gettoken"  # 修复：使用正确的API端点
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.kf_secret,
            "debug": 1  # 添加debug参数以支持hint值查询
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                
                # 详细日志
                logger.info(f"API响应状态码: {response.status_code}")
                logger.info(f"API响应内容: {response.text[:200]}")
                
                if response.status_code != 200:
                    logger.error(f"❌ API请求失败，状态码: {response.status_code}")
                    logger.error(f"可能原因：服务器网络无法访问企业微信API (qyapi.weixin.qq.com)")
                    logger.error(f"建议：检查网络连接或配置代理")
                    raise Exception(f"API请求失败: HTTP {response.status_code}")
                
                if not response.text or response.text.strip() == "":
                    logger.error(f"❌ API返回空内容")
                    raise Exception("API返回空内容")
                
                data = response.json()
                
                if data.get("errcode", 0) != 0:
                    logger.error(f"获取客服access_token失败: {data}")
                    raise Exception(f"获取客服access_token失败: {data.get('errmsg')}")
                
                self._access_token = data["access_token"]
                expires_in = data.get("expires_in", 7200)
                self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
                
                logger.info(f"✅ 成功获取客服access_token: {self._access_token[:20]}...")
                return self._access_token
        except Exception as e:
            logger.error(f"❌ 获取客服access_token异常: {e}")
            raise
    
    async def sync_message(self, open_kfid: str, token: str, cursor: str = "", limit: int = 100) -> Dict[str, Any]:
        """同步客服消息
        
        Args:
            open_kfid: 客服账号ID
            token: 消息token（从webhook事件中获取）
            cursor: 分页游标
            limit: 每页数量
            
        Returns:
            消息列表和下一页游标
        """
        access_token = await self.get_access_token()
        url = f"{self.base_url}/kf/sync_msg"
        
        data = {
            "open_kfid": open_kfid,
            "token": token,
            "limit": limit,
            "voice_format": 0
        }
        
        if cursor:
            data["cursor"] = cursor
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    params={"access_token": access_token, "debug": 1},
                    json=data
                )
                result = response.json()
                
                if result.get("errcode", 0) != 0:
                    logger.error(f"同步客服消息失败: {result}")
                    return {"msg_list": [], "next_cursor": ""}
                
                logger.info(f"成功同步 {len(result.get('msg_list', []))} 条客服消息")
                return result
        except Exception as e:
            logger.error(f"同步客服消息异常: {e}")
            return {"msg_list": [], "next_cursor": ""}
    
    async def send_message(
        self,
        open_kfid: str,
        external_userid: str,
        msg_type: str,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """发送客服消息
        
        Args:
            open_kfid: 客服账号ID
            external_userid: 外部用户ID
            msg_type: 消息类型 (text, image, voice, video, file, link, miniprogram, msgmenu)
            content: 消息内容
            
        Returns:
            API响应结果
        """
        access_token = await self.get_access_token()
        url = f"{self.base_url}/kf/send_msg"
        
        data = {
            "touser": external_userid,
            "open_kfid": open_kfid,
            "msgtype": msg_type,
            msg_type: content
        }
        
        logger.info(f"📤 准备发送消息 - API: {url}")
        logger.info(f"📤 请求数据: {data}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    params={"access_token": access_token, "debug": 1},
                    json=data
                )
                
                logger.info(f"📥 响应状态码: {response.status_code}")
                logger.info(f"📥 响应内容: {response.text[:300]}")
                
                result = response.json()
                
                if result.get("errcode", 0) != 0:
                    errcode = result.get("errcode")
                    errmsg = result.get("errmsg", "")
                    
                    # 详细的错误分析
                    if errcode == 45009:
                        logger.error(f"❌ API调用频率超限！")
                        logger.warning(f"💡 解决方法：")
                        logger.warning(f"   1. 等待 1-2 分钟后重试")
                        logger.warning(f"   2. 减少测试频率")
                        logger.warning(f"   3. 企业微信客服 API 限制: 每分钟约 20 次")
                    elif errcode == 40058:
                        logger.error(f"❌ 缺少必需参数 touser")
                        logger.error(f"   当前 touser: {external_userid}")
                    elif errcode == 95018:
                        logger.error(f"❌ 会话状态不允许发送消息")
                        logger.error(f"   可能原因: 会话在人工接待状态(state=3)或已结束(state=4)")
                    
                    logger.error(f"发送客服消息失败: {result}")
                else:
                    logger.info(f"✅ 成功发送客服消息给用户 {external_userid}")
                
                return result
        except Exception as e:
            logger.error(f"发送客服消息异常: {e}")
            return {"errcode": -1, "errmsg": str(e)}
    
    async def send_text_message(
        self,
        open_kfid: str,
        external_userid: str,
        content: str
    ) -> Dict[str, Any]:
        """发送文本消息（快捷方法）"""
        return await self.send_message(
            open_kfid,
            external_userid,
            "text",
            {"content": content}
        )
    
    async def service_state_trans(
        self,
        open_kfid: str,
        external_userid: str,
        service_state: int,
        servicer_userid: str = ""
    ) -> Dict[str, Any]:
        """接待会话状态变更
        
        Args:
            open_kfid: 客服账号ID
            external_userid: 外部用户ID
            service_state: 服务状态
                0: 未处理
                1: 人工接待
                2: 机器人接待
                3: 已结束
            servicer_userid: 接待人员userid（service_state=1时需要）
            
        Returns:
            API响应结果
        """
        access_token = await self.get_access_token()
        url = f"{self.base_url}/kf/service_state/trans"
        
        data = {
            "open_kfid": open_kfid,
            "external_userid": external_userid,
            "service_state": service_state
        }
        
        if servicer_userid:
            data["servicer_userid"] = servicer_userid
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    params={"access_token": access_token, "debug": 1},
                    json=data
                )
                result = response.json()
                
                if result.get("errcode", 0) != 0:
                    logger.error(f"变更会话状态失败: {result}")
                else:
                    # 官方文档: https://developer.work.weixin.qq.com/document/path/94669
                    state_name = {
                        0: "新接入待处理", 
                        1: "智能助手接待", 
                        2: "待接入池排队", 
                        3: "人工接待中", 
                        4: "已结束"
                    }.get(service_state, "未知")
                    logger.info(f"成功变更会话状态为「{state_name}」: {external_userid}")
                
                return result
        except Exception as e:
            logger.error(f"变更会话状态异常: {e}")
            return {"errcode": -1, "errmsg": str(e)}
    
    async def get_service_state(
        self,
        open_kfid: str,
        external_userid: str
    ) -> Dict[str, Any]:
        """获取会话状态
        
        Args:
            open_kfid: 客服账号ID
            external_userid: 外部用户ID
            
        Returns:
            会话状态信息
        """
        access_token = await self.get_access_token()
        url = f"{self.base_url}/kf/service_state/get"
        
        data = {
            "open_kfid": open_kfid,
            "external_userid": external_userid
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    params={"access_token": access_token, "debug": 1},
                    json=data
                )
                result = response.json()
                
                if result.get("errcode", 0) != 0:
                    logger.error(f"获取会话状态失败: {result}")
                else:
                    logger.info(f"成功获取会话状态: {external_userid}")
                
                return result
        except Exception as e:
            logger.error(f"获取会话状态异常: {e}")
            return {"errcode": -1, "errmsg": str(e)}
    
    async def get_account_list(self, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """获取客服账号列表
        
        Args:
            offset: 分页偏移
            limit: 每页数量
            
        Returns:
            客服账号列表
        """
        access_token = await self.get_access_token()
        url = f"{self.base_url}/kf/account/list"
        
        params = {
            "access_token": access_token,
            "offset": offset,
            "limit": limit,
            "debug": 1
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                result = response.json()
                
                if result.get("errcode", 0) != 0:
                    logger.error(f"获取客服账号列表失败: {result}")
                    return []
                
                accounts = result.get("account_list", [])
                logger.info(f"成功获取 {len(accounts)} 个客服账号")
                return accounts
        except Exception as e:
            logger.error(f"获取客服账号列表异常: {e}")
            return []

