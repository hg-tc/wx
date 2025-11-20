import httpx
import asyncio
from app.config import get_settings

async def check_state():
    """查询真实的会话状态"""
    settings = get_settings()
    
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
        
        print("=" * 70)
        print("查询会话状态 - 验证state定义")
        print("=" * 70)
        
        # 查询会话状态
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
        result = response.json()
        
        print(f"\n📊 API返回的完整数据:")
        print(f"   {result}")
        
        if result.get('errcode') == 0:
            service_state = result.get('service_state')
            servicer_userid = result.get('servicer_userid', '')
            
            print(f"\n🔍 解析:")
            print(f"   service_state = {service_state}")
            print(f"   servicer_userid = {servicer_userid}")
            
            print(f"\n💡 状态分析:")
            if service_state == 0:
                print("   state=0 => 新接入待处理（未分配）")
            elif service_state == 1:
                print("   state=1 => 由智能助手接待中")
            elif service_state == 2:
                print("   state=2 => 待接入池排队中")
            elif service_state == 3:
                print("   state=3 => 由人工接待中（有servicer_userid）")
                print(f"   接待人员: {servicer_userid}")
            elif service_state == 4:
                print("   state=4 => 已结束/已关闭")
            
            print(f"\n💬 是否可以发送消息？")
            if service_state in [0, 1]:
                print("   ✅ 可以 - 可调用send_msg发送")
            elif service_state == 3:
                print("   ✅ 可以 - 人工接待中，可以发送")
            else:
                print("   ❌ 不可以 - 此状态无法发送消息")
        else:
            print(f"\n❌ 查询失败: {result}")
        
        print("=" * 70)

asyncio.run(check_state())
