"""企业微信消息接收处理"""
import xmltodict
from typing import Dict, Any, Optional
from app.wecom.auth import WXBizMsgCrypt
from app.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger()


class WeComWebhook:
    """企业微信Webhook处理器"""
    
    def __init__(self):
        self.crypto = WXBizMsgCrypt(
            settings.WECOM_TOKEN,
            settings.WECOM_ENCODING_AES_KEY,
            settings.WECOM_CORP_ID
        )
    
    def parse_message(self, msg_signature: str, timestamp: str, nonce: str, 
                     encrypted_data: str) -> Optional[Dict[str, Any]]:
        """解析企业微信消息"""
        try:
            # 解析XML
            xml_dict = xmltodict.parse(encrypted_data)
            encrypted_msg = xml_dict['xml']['Encrypt']
            
            # 解密消息
            decrypted_xml = self.crypto.decrypt_message(
                msg_signature, timestamp, nonce, encrypted_msg
            )
            
            if not decrypted_xml:
                return None
            
            # 解析解密后的XML
            message_dict = xmltodict.parse(decrypted_xml)
            message = message_dict.get('xml', {})
            
            logger.info(f"接收到消息: {message.get('MsgType')} from {message.get('FromUserName')}")
            return message
            
        except Exception as e:
            logger.error(f"解析消息失败: {e}")
            return None
    
    def build_reply(self, to_user: str, from_user: str, content: str, 
                   nonce: str, timestamp: str) -> str:
        """构建回复消息"""
        reply_xml = f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{timestamp}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>"""
        
        # 加密
        encrypted, signature = self.crypto.encrypt_message(reply_xml, nonce, timestamp)
        
        # 构建返回XML
        response_xml = f"""<xml>
<Encrypt><![CDATA[{encrypted}]]></Encrypt>
<MsgSignature><![CDATA[{signature}]]></MsgSignature>
<TimeStamp>{timestamp}</TimeStamp>
<Nonce><![CDATA[{nonce}]]></Nonce>
</xml>"""
        
        return response_xml
    
    def extract_text_message(self, message: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """提取文本消息内容"""
        if message.get('MsgType') != 'text':
            return None
        
        return {
            'from_user': message.get('FromUserName'),
            'to_user': message.get('ToUserName'),
            'content': message.get('Content'),
            'msg_id': message.get('MsgId'),
            'agent_id': message.get('AgentID')
        }
    
    def extract_event_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """提取事件消息内容"""
        if message.get('MsgType') != 'event':
            return None
        
        return {
            'from_user': message.get('FromUserName'),
            'event': message.get('Event'),
            'event_key': message.get('EventKey'),
            'agent_id': message.get('AgentID')
        }
    
    def extract_kf_event(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """提取客服事件消息
        
        客服消息事件结构：
        <xml>
            <ToUserName>企业CorpID</ToUserName>
            <CreateTime>1348831860</CreateTime>
            <MsgType>event</MsgType>
            <Event>kf_msg_or_event</Event>
            <Token>消息token</Token>
            <OpenKfId>客服账号ID</OpenKfId>
        </xml>
        """
        if message.get('MsgType') != 'event':
            return None
        
        if message.get('Event') != 'kf_msg_or_event':
            return None
        
        result = {
            'event': 'kf_msg_or_event',
            'token': message.get('Token'),
            'open_kfid': message.get('OpenKfId'),
            'create_time': message.get('CreateTime')
        }
        
        logger.info(f"✅ 提取到客服事件 - OpenKfId: {result['open_kfid']}, Token: {result['token'][:20]}...")
        return result
    
    def is_kf_message(self, message: Dict[str, Any]) -> bool:
        """判断是否为客服消息"""
        return (message.get('MsgType') == 'event' and 
                message.get('Event') == 'kf_msg_or_event')

