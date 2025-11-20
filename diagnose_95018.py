#!/usr/bin/env python3
"""
诊断95018错误的真正原因
"""
import httpx
import asyncio
from app.config import get_settings

async def diagnose():
    settings = get_settings()
    
    print("=" * 70)
    print("🔍 深入诊断95018错误")
    print("=" * 70)
    
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
        token = data["access_token"]
        
        print(f"\n1️⃣ 获取access_token: ✅")
        print(f"   Token: {token[:30]}...")
        
        # 查询会话状态
        print(f"\n2️⃣ 查询会话状态...")
        state_url = "https://qyapi.weixin.qq.com/cgi-bin/kf/service_state/get"
        state_data = {
            "open_kfid": "wk7lKAVwAAADCtArVetgUpxDBFQHef6A",
            "external_userid": "wm7lKAVwAAG68dSOO7G4EVpN1eScOUPw"
        }
        
        response = await client.post(
            state_url,
            params={"access_token": token, "debug": 1},
            json=state_data
        )
        state_result = response.json()
        
        print(f"   完整响应: {state_result}")
        
        service_state = state_result.get('service_state', -1)
        servicer_userid = state_result.get('servicer_userid', '')
        
        print(f"\n   📊 service_state = {service_state}")
        print(f"   👤 servicer_userid = {servicer_userid}")
        
        # 获取客服账号列表
        print(f"\n3️⃣ 获取客服账号信息...")
        account_url = "https://qyapi.weixin.qq.com/cgi-bin/kf/account/list"
        
        response = await client.post(
            account_url,
            params={"access_token": token, "debug": 1},
            json={"offset": 0, "limit": 100}
        )
        account_result = response.json()
        
        if account_result.get('errcode') == 0:
            accounts = account_result.get('account_list', [])
            for acc in accounts:
                if acc.get('open_kfid') == "wk7lKAVwAAADCtArVetgUpxDBFQHef6A":
                    print(f"   找到客服账号:")
                    print(f"   - 名称: {acc.get('name')}")
                    print(f"   - open_kfid: {acc.get('open_kfid')}")
        
        # 测试发送（简化消息）
        print(f"\n4️⃣ 尝试发送最简单的消息...")
        send_url = "https://qyapi.weixin.qq.com/cgi-bin/kf/send_msg"
        send_data = {
            "touser": "wm7lKAVwAAG68dSOO7G4EVpN1eScOUPw",
            "open_kfid": "wk7lKAVwAAADCtArVetgUpxDBFQHef6A",
            "msgtype": "text",
            "text": {"content": "测试"}
        }
        
        response = await client.post(
            send_url,
            params={"access_token": token, "debug": 1},
            json=send_data
        )
        send_result = response.json()
        
        print(f"   发送结果: {send_result}")
        
        # 分析
        print(f"\n" + "=" * 70)
        print("📊 分析结果")
        print("=" * 70)
        
        if send_result.get('errcode') == 0:
            print("✅ 发送成功！")
        elif send_result.get('errcode') == 95018:
            print("❌ 仍然是95018错误")
            print("\n可能的原因：")
            print("1. 会话虽然是state=3，但可能有其他限制")
            print("2. servicer_userid='ZhangSuQuan' 可能不是通过API添加的")
            print("3. 可能需要在企业微信后台设置'允许API发送消息'")
            print("4. 会话可能处于特殊状态（如转接中、暂停等）")
            
            print("\n🔍 建议检查：")
            print("- 企业微信后台 > 客服 > 接待人员权限设置")
            print("- 是否启用了'仅人工可发送'限制")
            print("- ZhangSuQuan 是否有通过API发送消息的权限")
        else:
            print(f"⚠️  其他错误: {send_result.get('errcode')} - {send_result.get('errmsg')}")
        
        # 查询hint信息
        if send_result.get('errcode') == 95018:
            hint = send_result.get('errmsg', '')
            if 'hint:' in hint:
                hint_id = hint.split('hint:')[1].split(',')[0].strip()
                print(f"\n🔗 查看详细错误说明:")
                print(f"   https://open.work.weixin.qq.com/devtool/query?e=95018")
                print(f"   Hint ID: {hint_id}")
        
        print("=" * 70)

asyncio.run(diagnose())

