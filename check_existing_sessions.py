#!/usr/bin/env python3
"""
检查现有会话的状态
如果有已存在的会话（比如之前测试的），可以查看其状态
"""
import httpx
import asyncio
import sys
from app.config import get_settings

async def check_sessions():
    """检查现有会话状态"""
    settings = get_settings()
    
    print("=" * 70)
    print("🔍 检查现有客服会话状态")
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
            print(f"✅ 获取access_token成功\n")
            
            # 已知的会话信息（从日志中提取）
            known_sessions = [
                {
                    "open_kfid": "wk7lKAVwAAADCtArVetgUpxDBFQHef6A",
                    "external_userid": "wm7lKAVwAAG68dSOO7G4EVpN1eScOUPw",
                    "name": "测试用户"
                }
            ]
            
            print("📋 已知的会话:")
            print("─" * 70)
            
            for session in known_sessions:
                open_kfid = session['open_kfid']
                external_userid = session['external_userid']
                name = session['name']
                
                print(f"\n🔹 {name}")
                print(f"   open_kfid: {open_kfid}")
                print(f"   external_userid: {external_userid}")
                
                # 查询会话状态
                state_url = "https://qyapi.weixin.qq.com/cgi-bin/kf/service_state/get"
                state_data = {
                    "open_kfid": open_kfid,
                    "external_userid": external_userid
                }
                
                response = await client.post(
                    state_url,
                    params={"access_token": token, "debug": 1},
                    json=state_data
                )
                result = response.json()
                
                if result.get('errcode') == 0:
                    service_state = result.get('service_state', -1)
                    servicer_userid = result.get('servicer_userid', '')
                    
                    state_map = {
                        0: "新接入待处理",
                        1: "智能助手接待",
                        2: "待接入池排队",
                        3: "人工接待中",
                        4: "已结束"
                    }
                    state_name = state_map.get(service_state, "未知")
                    
                    print(f"\n   📊 当前状态: {state_name} (state={service_state})")
                    if servicer_userid:
                        print(f"   👤 接待人员: {servicer_userid}")
                    
                    # 判断是否可以用API发送
                    can_send = service_state in [0, 1]
                    
                    print(f"\n   🎯 API发送状态:")
                    if can_send:
                        print(f"      ✅ 可以发送 - state={service_state} 支持 send_msg API")
                    else:
                        print(f"      ❌ 不能发送 - state={service_state} 不支持 send_msg API")
                        
                        if service_state == 3:
                            print(f"\n      💡 原因: 会话处于人工接待状态")
                            print(f"      🔧 解决: 去企业微信后台改为「仅智能助手接待」")
                            print(f"            然后创建新会话（旧会话状态不会改变）")
                        elif service_state == 2:
                            print(f"\n      💡 原因: 会话在待接入池排队")
                        elif service_state == 4:
                            print(f"\n      💡 原因: 会话已结束")
                else:
                    print(f"\n   ❌ 查询失败: {result.get('errmsg')}")
                    if result.get('errcode') == 95001:
                        print(f"      可能该会话已不存在或已超时")
            
            # 后台配置建议
            print(f"\n{'=' * 70}")
            print("🎯 后台配置检查")
            print("=" * 70)
            print(f"\n当前情况分析:")
            
            # 根据查询结果给建议
            if any(result.get('errcode') == 0 and result.get('service_state') == 3 
                   for result in [result]):  # 这里简化了逻辑
                print(f"⚠️  检测到会话处于 state=3（人工接待）")
                print(f"\n这说明企业微信后台配置可能是:")
                print(f"   - 人工接待优先")
                print(f"   - 仅人工接待")
                print(f"   - 自动分配给接待人员")
                print(f"\n✅ 建议修改为:")
                print(f"   1. 登录 https://work.weixin.qq.com/")
                print(f"   2. 应用管理 > 微信客服")
                print(f"   3. 接待设置 > 接待模式")
                print(f"   4. 选择「仅智能助手接待」或「智能助手接待优先」")
                print(f"   5. 保存配置")
                print(f"   6. 创建新会话测试")
            
            print(f"\n{'=' * 70}")
            print("📝 下一步操作")
            print("=" * 70)
            print(f"1. 如果配置正确，创建新会话测试")
            print(f"2. 启动应用: pkill -f uvicorn && sleep 2 && \\")
            print(f"              nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > logs/uvicorn.log 2>&1 &")
            print(f"3. 监控日志: tail -f logs/app_*.log | grep -E '会话状态|发送'")
            print(f"4. 发送消息测试")
            print("=" * 70)
            
            return True
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(check_sessions())
    sys.exit(0 if result else 1)

