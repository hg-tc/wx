"""匹配通知"""
from typing import Dict, Any, List
from app.wecom.client import WeComClient
from app.wecom.message_builder import MessageBuilder
from app.utils.logger import get_logger

logger = get_logger()


class MatchNotification:
    """匹配通知"""
    
    def __init__(self):
        self.wecom_client = WeComClient()
        self.message_builder = MessageBuilder()
    
    async def notify_matches(
        self,
        wecom_user_id: str,
        matches: List[Dict[str, Any]]
    ) -> bool:
        """通知用户匹配结果"""
        try:
            if not matches:
                message = "暂未找到匹配的服务，我们会继续为您寻找。"
            else:
                message = self.message_builder.build_service_match_message(matches)
            
            await self.wecom_client.send_text_message(wecom_user_id, message)
            logger.info(f"发送匹配通知给用户 {wecom_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"发送匹配通知失败: {e}")
            return False
    
    async def notify_service_recorded(
        self,
        wecom_user_id: str,
        service_type: str,
        title: str
    ) -> bool:
        """通知服务录入成功"""
        try:
            message = self.message_builder.build_service_recorded_message(service_type, title)
            await self.wecom_client.send_text_message(wecom_user_id, message)
            logger.info(f"发送服务录入通知给用户 {wecom_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"发送服务录入通知失败: {e}")
            return False
    
    async def notify_match_accepted(
        self,
        wecom_user_id: str,
        service_info: Dict[str, Any],
        contact_info: Dict[str, Any]
    ) -> bool:
        """通知匹配已被接受，发送联系方式"""
        try:
            message = f"🎉 好消息！对方对您的服务感兴趣\n\n"
            message += f"服务：{service_info.get('title', '未知服务')}\n"
            message += f"联系方式：\n"
            
            if contact_info.get('phone'):
                message += f"📞 电话：{contact_info['phone']}\n"
            if contact_info.get('wechat'):
                message += f"💬 微信：{contact_info['wechat']}\n"
            if contact_info.get('email'):
                message += f"📧 邮箱：{contact_info['email']}\n"
            
            message += "\n请及时联系对方！"
            
            await self.wecom_client.send_text_message(wecom_user_id, message)
            logger.info(f"发送匹配接受通知给用户 {wecom_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"发送匹配接受通知失败: {e}")
            return False

