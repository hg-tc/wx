#!/usr/bin/env python3
"""
检查客服会话状态 - 应用启动时运行
"""
import httpx
import asyncio
import sys
from app.config import get_settings

async def check_state():
    """检查当前会话状态"""
    settings = get_settings()
    
    print("=" * 70)
    print("🔍 检查客服会话状态")
    print("=" * 70)
    
    try:
        # 获取token
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            "corpid": settings.WECOM_CORP_ID,
            "corpsecret": settings.WECOM_KF_SECRET,
            "debug": 1
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            data = response.json()
            
            if data.get('errcode', 0) != 0:
                print(f"❌ 获取token失败: {data}")
                return False
            
            token = data["access_token"]
            print(f"✅ 获取access_token成功")
            
            # 获取客服账号列表
            print(f"\n📋 获取客服账号...")
            account_url = "https://qyapi.weixin.qq.com/cgi-bin/kf/account/list"
            
            response = await client.post(
                account_url,
                params={"access_token": token, "debug": 1},
                json={"offset": 0, "limit": 100}
            )
            account_result = response.json()
            
            if account_result.get('errcode', 0) != 0:
                print(f"❌ 获取账号失败: {account_result}")
                return False
            
            accounts = account_result.get('account_list', [])
            if not accounts:
                print("⚠️  没有找到客服账号")
                return False
            
            print(f"✅ 找到 {len(accounts)} 个客服账号")
            
            # 检查每个账号的配置
            for acc in accounts:
                open_kfid = acc.get('open_kfid')
                name = acc.get('name')
                
                print(f"\n{'─' * 70}")
                print(f"📱 客服账号: {name}")
                print(f"   open_kfid: {open_kfid}")
                
                # 注意：无法直接查询"未来会话"的状态
                # 只能查询已存在的会话
                print(f"\n💡 说明:")
                print(f"   - 会话状态只能在用户发送消息后查询")
                print(f"   - 新会话的状态由企业微信后台配置决定")
                print(f"   - 无法提前知道下一个会话会进入什么状态")
                
            # 给出配置建议
            print(f"\n{'=' * 70}")
            print("🎯 后台配置建议")
            print("=" * 70)
            print(f"\n如果要让API能自动回复，需要确保:")
            print(f"1. 企业微信后台 > 应用管理 > 微信客服")
            print(f"2. 接待设置 > 接待模式")
            print(f"3. 选择:")
            print(f"   ✅ 仅智能助手接待")
            print(f"   或")
            print(f"   ✅ 智能助手接待优先")
            print(f"\n这样新会话会进入 state=1，API就可以发送消息了")
            
            # 测试建议
            print(f"\n{'=' * 70}")
            print("📝 测试步骤")
            print("=" * 70)
            print(f"1. 修改企业微信后台配置")
            print(f"2. 删除/退出当前客服会话（重要！）")
            print(f"3. 重新进入客服发送消息")
            print(f"4. 查看日志：")
            print(f"   tail -f logs/app_*.log | grep '会话状态'")
            print(f"\n预期日志:")
            print(f"   📊 当前会话状态: 智能助手接待 (state=1)  ← 正确！")
            print(f"   ✅ 成功发送客服消息")
            
            print("=" * 70)
            return True
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(check_state())
    sys.exit(0 if result else 1)

