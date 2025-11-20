#!/usr/bin/env python3
"""测试企业微信回调配置"""
import sys
import os
sys.path.insert(0, '/root/wx')

from app.config import get_settings
from app.wecom.auth import WXBizMsgCrypt
import hashlib
import time

def test_config():
    """测试配置是否正确"""
    print("=" * 60)
    print("企业微信配置测试")
    print("=" * 60)
    
    settings = get_settings()
    
    print(f"\n1. 配置信息:")
    print(f"   CORP_ID: {settings.WECOM_CORP_ID}")
    print(f"   AGENT_ID: {settings.WECOM_AGENT_ID}")
    print(f"   TOKEN: {settings.WECOM_TOKEN}")
    print(f"   ENCODING_AES_KEY 长度: {len(settings.WECOM_ENCODING_AES_KEY)}")
    
    # 检查AES Key长度
    if len(settings.WECOM_ENCODING_AES_KEY) != 43:
        print(f"   ❌ ENCODING_AES_KEY 长度错误！应该是43位，当前是 {len(settings.WECOM_ENCODING_AES_KEY)} 位")
        return False
    else:
        print(f"   ✅ ENCODING_AES_KEY 长度正确（43位）")
    
    # 测试加解密
    print(f"\n2. 测试加解密功能:")
    try:
        crypto = WXBizMsgCrypt(
            settings.WECOM_TOKEN,
            settings.WECOM_ENCODING_AES_KEY,
            settings.WECOM_CORP_ID
        )
        print("   ✅ WXBizMsgCrypt 初始化成功")
        
        # 测试加密解密
        test_msg = "test_message_123"
        nonce = "test_nonce"
        timestamp = str(int(time.time()))
        
        encrypted, signature = crypto.encrypt_message(test_msg, nonce, timestamp)
        print(f"   ✅ 消息加密成功")
        
        decrypted = crypto.decrypt_message(signature, timestamp, nonce, encrypted)
        if decrypted == test_msg:
            print(f"   ✅ 消息解密成功，内容匹配")
        else:
            print(f"   ❌ 消息解密失败，内容不匹配")
            return False
            
    except Exception as e:
        print(f"   ❌ 加解密测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n3. 模拟企业微信URL验证:")
    try:
        # 模拟企业微信发送的验证参数
        timestamp = str(int(time.time()))
        nonce = "test_nonce_123"
        echostr_plain = "test_echo_string"
        
        # 加密echostr
        encrypted_echostr, _ = crypto.encrypt_message(echostr_plain, nonce, timestamp)
        
        # 生成签名
        signature = crypto._generate_signature(timestamp, nonce, encrypted_echostr)
        
        print(f"   模拟参数:")
        print(f"   - timestamp: {timestamp}")
        print(f"   - nonce: {nonce}")
        print(f"   - echostr: {encrypted_echostr[:50]}...")
        print(f"   - signature: {signature}")
        
        # 验证签名并解密
        result = crypto.verify_signature(signature, timestamp, nonce, encrypted_echostr)
        
        if result == echostr_plain:
            print(f"   ✅ URL验证模拟成功")
        else:
            print(f"   ❌ URL验证失败: 期望={echostr_plain}, 实际={result}")
            return False
            
    except Exception as e:
        print(f"   ❌ URL验证测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n{'=' * 60}")
    print("✅ 所有测试通过！配置正确！")
    print("=" * 60)
    return True


def generate_test_curl():
    """生成测试curl命令"""
    settings = get_settings()
    crypto = WXBizMsgCrypt(
        settings.WECOM_TOKEN,
        settings.WECOM_ENCODING_AES_KEY,
        settings.WECOM_CORP_ID
    )
    
    timestamp = str(int(time.time()))
    nonce = "test_nonce"
    echostr_plain = "test_echo"
    
    encrypted_echostr, _ = crypto.encrypt_message(echostr_plain, nonce, timestamp)
    signature = crypto._generate_signature(timestamp, nonce, encrypted_echostr)
    
    print("\n" + "=" * 60)
    print("测试 curl 命令（用于测试本地服务器）")
    print("=" * 60)
    print(f"""
curl -X GET "http://localhost:8000/api/v1/wecom/callback?\\
msg_signature={signature}&\\
timestamp={timestamp}&\\
nonce={nonce}&\\
echostr={encrypted_echostr}"
""")
    print(f"期望返回: {echostr_plain}")
    print("=" * 60)


if __name__ == "__main__":
    if test_config():
        generate_test_curl()
        print("\n💡 提示:")
        print("1. 启动应用: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("2. 运行上面的 curl 命令测试本地回调")
        print("3. 配置企业微信回调URL时，请使用以下信息:")
        print(f"   Token: {get_settings().WECOM_TOKEN}")
        print(f"   EncodingAESKey: {get_settings().WECOM_ENCODING_AES_KEY}")
    else:
        print("\n❌ 配置有误，请检查 .env 文件")
        sys.exit(1)

