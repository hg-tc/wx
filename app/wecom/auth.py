"""企业微信消息签名验证"""
import hashlib
import struct
import socket
from Crypto.Cipher import AES
import base64
import xml.etree.ElementTree as ET
from typing import Tuple, Optional
from app.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger()


class WXBizMsgCrypt:
    """企业微信消息加解密"""
    
    def __init__(self, token: str, encoding_aes_key: str, corp_id: str):
        self.token = token
        self.encoding_aes_key = encoding_aes_key
        self.corp_id = corp_id
        self.key = base64.b64decode(encoding_aes_key + "=")
        
    def verify_signature(self, signature: str, timestamp: str, nonce: str, echo_str: str) -> Optional[str]:
        """验证签名并解密echo_str"""
        sign = self._generate_signature(timestamp, nonce, echo_str)
        if sign != signature:
            logger.error(f"签名验证失败: expected={sign}, got={signature}")
            return None
        
        # 解密echo_str
        try:
            decrypted = self._decrypt(echo_str)
            return decrypted
        except Exception as e:
            logger.error(f"解密echo_str失败: {e}")
            return None
    
    def decrypt_message(self, msg_signature: str, timestamp: str, nonce: str, encrypted_msg: str) -> Optional[str]:
        """解密消息"""
        # 验证签名
        sign = self._generate_signature(timestamp, nonce, encrypted_msg)
        if sign != msg_signature:
            logger.error(f"消息签名验证失败: expected={sign}, got={msg_signature}")
            return None
        
        # 解密消息
        try:
            xml_content = self._decrypt(encrypted_msg)
            return xml_content
        except Exception as e:
            logger.error(f"解密消息失败: {e}")
            return None
    
    def encrypt_message(self, reply_msg: str, nonce: str, timestamp: str) -> Tuple[str, str]:
        """加密消息"""
        encrypted = self._encrypt(reply_msg)
        signature = self._generate_signature(timestamp, nonce, encrypted)
        return encrypted, signature
    
    def _generate_signature(self, timestamp: str, nonce: str, encrypt: str) -> str:
        """生成签名"""
        sort_list = [self.token, timestamp, nonce, encrypt]
        sort_list.sort()
        sha = hashlib.sha1()
        sha.update("".join(sort_list).encode())
        return sha.hexdigest()
    
    def _encrypt(self, text: str) -> str:
        """加密消息"""
        text = text.encode()
        # 随机16字节
        import os
        random_bytes = os.urandom(16)
        
        # 消息长度
        msg_len = struct.pack("I", socket.htonl(len(text)))
        
        # 拼接
        plain_text = random_bytes + msg_len + text + self.corp_id.encode()
        
        # PKCS7填充
        block_size = 32
        padding_size = block_size - len(plain_text) % block_size
        padding = bytes([padding_size] * padding_size)
        plain_text = plain_text + padding
        
        # AES加密
        cipher = AES.new(self.key, AES.MODE_CBC, self.key[:16])
        encrypted = cipher.encrypt(plain_text)
        
        return base64.b64encode(encrypted).decode()
    
    def _decrypt(self, encrypted_text: str) -> str:
        """解密消息"""
        encrypted = base64.b64decode(encrypted_text)
        
        # AES解密
        cipher = AES.new(self.key, AES.MODE_CBC, self.key[:16])
        decrypted = cipher.decrypt(encrypted)
        
        # 去除填充
        pad = decrypted[-1]
        if isinstance(pad, int):
            padding_size = pad
        else:
            padding_size = ord(pad)
        decrypted = decrypted[:-padding_size]
        
        # 提取消息
        msg_len_bytes = decrypted[16:20]
        msg_len = socket.ntohl(struct.unpack("I", msg_len_bytes)[0])
        content = decrypted[20:20 + msg_len].decode()
        
        return content


def verify_url_signature(signature: str, timestamp: str, nonce: str, echostr: str) -> Optional[str]:
    """验证URL签名（用于企业微信回调URL验证）"""
    crypto = WXBizMsgCrypt(
        settings.WECOM_TOKEN,
        settings.WECOM_ENCODING_AES_KEY,
        settings.WECOM_CORP_ID
    )
    return crypto.verify_signature(signature, timestamp, nonce, echostr)

