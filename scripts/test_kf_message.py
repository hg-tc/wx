#!/usr/bin/env python3
"""测试客服消息处理"""
import sys
import os
import asyncio

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.wecom.kf_client import KfClient
from app.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger()


async def test_get_account_list():
    """测试获取客服账号列表"""
    print("=" * 60)
    print("📋 测试：获取客服账号列表")
    print("=" * 60)
    print()
    
    kf_client = KfClient()
    
    try:
        accounts = await kf_client.get_account_list()
        
        if accounts:
            print(f"✅ 成功获取 {len(accounts)} 个客服账号：")
            print()
            
            for idx, account in enumerate(accounts, 1):
                print(f"客服 #{idx}")
                print(f"  名称: {account.get('name')}")
                print(f"  OpenKfId: {account.get('open_kfid')}")
                print(f"  头像: {account.get('avatar', '无')}")
                print()
        else:
            print("❌ 未获取到客服账号")
            print()
            print("请确认：")
            print("  1. 已在企业微信后台创建客服账号")
            print("  2. WECOM_SECRET 或 WECOM_KF_SECRET 配置正确")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_send_message():
    """测试发送客服消息"""
    print("=" * 60)
    print("📨 测试：发送客服消息")
    print("=" * 60)
    print()
    
    # 检查必要配置
    if not settings.WECOM_KF_ACCOUNT_ID:
        print("❌ 未配置 WECOM_KF_ACCOUNT_ID")
        print()
        print("请先：")
        print("  1. 发送一条测试消息到客服")
        print("  2. 从日志中获取 OpenKfId")
        print("  3. 配置到 .env 文件")
        return
    
    external_userid = input("请输入外部用户ID (external_userid): ").strip()
    
    if not external_userid:
        print("❌ 未输入外部用户ID")
        print()
        print("提示：")
        print("  1. 在微信中发送一条消息到客服")
        print("  2. 从日志中获取 external_userid")
        print("  3. 使用该ID测试发送消息")
        return
    
    message = input("请输入要发送的消息内容 [默认: 你好，这是一条测试消息]: ").strip()
    if not message:
        message = "你好，这是一条测试消息"
    
    print()
    print(f"发送消息到: {external_userid}")
    print(f"消息内容: {message}")
    print()
    
    kf_client = KfClient()
    
    try:
        result = await kf_client.send_text_message(
            settings.WECOM_KF_ACCOUNT_ID,
            external_userid,
            message
        )
        
        if result.get('errcode', 0) == 0:
            print("✅ 消息发送成功！")
            print()
            print("请在微信中查看是否收到消息")
        else:
            print(f"❌ 消息发送失败: {result}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_service_state():
    """测试会话状态变更"""
    print("=" * 60)
    print("🔄 测试：会话状态变更")
    print("=" * 60)
    print()
    
    if not settings.WECOM_KF_ACCOUNT_ID:
        print("❌ 未配置 WECOM_KF_ACCOUNT_ID")
        return
    
    external_userid = input("请输入外部用户ID (external_userid): ").strip()
    
    if not external_userid:
        print("❌ 未输入外部用户ID")
        return
    
    print()
    print("会话状态选项：")
    print("  0 - 未处理")
    print("  1 - 人工接待")
    print("  2 - 机器人接待")
    print("  3 - 已结束")
    print()
    
    state_input = input("请选择状态 [默认: 2-机器人接待]: ").strip()
    service_state = int(state_input) if state_input.isdigit() else 2
    
    print()
    print(f"设置用户 {external_userid} 的会话状态为: {service_state}")
    print()
    
    kf_client = KfClient()
    
    try:
        result = await kf_client.service_state_trans(
            settings.WECOM_KF_ACCOUNT_ID,
            external_userid,
            service_state
        )
        
        if result.get('errcode', 0) == 0:
            print("✅ 会话状态变更成功！")
        else:
            print(f"❌ 会话状态变更失败: {result}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主菜单"""
    while True:
        print()
        print("=" * 60)
        print("🧪 企业微信客服功能测试")
        print("=" * 60)
        print()
        print("当前配置：")
        print(f"  WECOM_CORP_ID: {settings.WECOM_CORP_ID}")
        print(f"  WECOM_KF_ACCOUNT_ID: {settings.WECOM_KF_ACCOUNT_ID or '未配置'}")
        print()
        print("请选择测试项：")
        print("  1. 获取客服账号列表")
        print("  2. 发送客服消息")
        print("  3. 变更会话状态")
        print("  0. 退出")
        print()
        
        choice = input("请输入选项 [1-3, 0退出]: ").strip()
        print()
        
        if choice == "1":
            await test_get_account_list()
        elif choice == "2":
            await test_send_message()
        elif choice == "3":
            await test_service_state()
        elif choice == "0":
            print("👋 退出测试")
            break
        else:
            print("❌ 无效选项，请重新选择")
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 测试中断")

