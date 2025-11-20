#!/usr/bin/env python3
"""获取企业微信客服账号信息"""
import sys
import os
import asyncio
import httpx

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger()


async def get_kf_access_token():
    """获取客服专用access_token"""
    url = "https://qyapi.weixin.qq.com/cgi-bin/token"
    params = {
        "corpid": settings.WECOM_CORP_ID,
        "corpsecret": settings.WECOM_SECRET  # 使用客服应用的Secret
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            
            # 调试信息
            print(f"  状态码: {response.status_code}")
            print(f"  响应内容: {response.text[:200]}...")
            
            if response.status_code != 200:
                logger.error(f"❌ HTTP请求失败: {response.status_code}")
                return None
            
            data = response.json()
            
            if data.get("errcode") != 0:
                logger.error(f"❌ 获取access_token失败: {data}")
                return None
            
            return data["access_token"]
    except Exception as e:
        logger.error(f"❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return None


async def get_kf_account_list(access_token):
    """获取客服账号列表"""
    url = "https://qyapi.weixin.qq.com/cgi-bin/kf/account/list"
    params = {
        "access_token": access_token,
        "offset": 0,
        "limit": 100
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        if data.get("errcode") != 0:
            logger.error(f"❌ 获取客服账号列表失败: {data}")
            return None
        
        return data.get("account_list", [])


async def main():
    """主函数"""
    print("=" * 60)
    print("🔍 正在获取企业微信客服账号信息...")
    print("=" * 60)
    print()
    
    # 1. 获取access_token
    print("📡 步骤1: 获取access_token...")
    token = await get_kf_access_token()
    
    if not token:
        print("❌ 获取access_token失败！")
        print()
        print("请检查 .env 文件中的配置：")
        print("  - WECOM_CORP_ID: 企业ID")
        print("  - WECOM_SECRET: 客服应用的Secret")
        return
    
    print(f"✅ 成功获取access_token: {token[:20]}...")
    print()
    
    # 2. 获取客服账号列表
    print("📡 步骤2: 获取客服账号列表...")
    accounts = await get_kf_account_list(token)
    
    if not accounts:
        print("❌ 未找到任何客服账号！")
        print()
        print("请在企业微信管理后台确认：")
        print("  1. 已创建客服应用")
        print("  2. 已添加客服账号")
        return
    
    print(f"✅ 找到 {len(accounts)} 个客服账号")
    print()
    
    # 3. 显示详细信息
    print("=" * 60)
    print("📋 客服账号详细信息:")
    print("=" * 60)
    print()
    
    for idx, account in enumerate(accounts, 1):
        print(f"客服账号 #{idx}")
        print(f"  名称: {account.get('name', '未知')}")
        print(f"  OpenKfId: {account.get('open_kfid', '未知')}")
        print(f"  头像: {account.get('avatar', '无')}")
        print(f"  管理权限: {'是' if account.get('manage_privilege') else '否'}")
        print()
    
    # 4. 生成配置建议
    if len(accounts) > 0:
        first_account = accounts[0]
        open_kfid = first_account.get('open_kfid')
        
        print("=" * 60)
        print("✅ 配置建议:")
        print("=" * 60)
        print()
        print("请将以下配置添加到 .env 文件：")
        print()
        print(f"WECOM_KF_ACCOUNT_ID={open_kfid}")
        print()
        
        if len(accounts) > 1:
            print("⚠️  注意: 你有多个客服账号，请选择需要使用的账号ID")
            print()


if __name__ == "__main__":
    asyncio.run(main())

