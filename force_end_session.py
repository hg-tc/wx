#!/usr/bin/env python3
"""
强制结束当前会话
将 state=3 转为 state=4（已结束）
然后用户重新发消息，会创建新会话
"""
import httpx
import asyncio
import sys
from app.config import get_settings

async def end_session():
    """结束当前会话"""
    settings = get_settings()
    
    print("=" * 70)
    print("🔧 强制结束客服会话")
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
            
            # 已知的会话信息
            open_kfid = "wk7lKAVwAAADCtArVetgUpxDBFQHef6A"
            external_userid = "wm7lKAVwAAG68dSOO7G4EVpN1eScOUPw"
            
            print("📋 目标会话:")
            print(f"   open_kfid: {open_kfid}")
            print(f"   external_userid: {external_userid}")
            
            # 1. 先查询当前状态
            print(f"\n📊 步骤1: 查询当前状态")
            print("─" * 70)
            
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
            state_result = response.json()
            
            if state_result.get('errcode', 0) != 0:
                print(f"❌ 查询状态失败: {state_result}")
                return False
            
            service_state = state_result.get('service_state', -1)
            servicer_userid = state_result.get('servicer_userid', '')
            
            state_map = {
                0: "新接入待处理",
                1: "智能助手接待",
                2: "待接入池排队",
                3: "人工接待中",
                4: "已结束"
            }
            state_name = state_map.get(service_state, "未知")
            
            print(f"✅ 当前状态: {state_name} (state={service_state})")
            if servicer_userid:
                print(f"   接待人员: {servicer_userid}")
            
            # 2. 尝试结束会话（转为state=4）
            print(f"\n🔧 步骤2: 尝试结束会话 (state={service_state} → state=4)")
            print("─" * 70)
            
            trans_url = "https://qyapi.weixin.qq.com/cgi-bin/kf/service_state/trans"
            trans_data = {
                "open_kfid": open_kfid,
                "external_userid": external_userid,
                "service_state": 4  # 4 = 已结束
            }
            
            # 如果当前是state=3，可能需要servicer_userid
            if service_state == 3 and servicer_userid:
                trans_data['servicer_userid'] = servicer_userid
                print(f"💡 当前是人工接待状态，添加 servicer_userid: {servicer_userid}")
            
            print(f"📤 请求数据: {trans_data}")
            
            response = await client.post(
                trans_url,
                params={"access_token": token, "debug": 1},
                json=trans_data
            )
            trans_result = response.json()
            
            print(f"📥 响应: {trans_result}")
            
            if trans_result.get('errcode') == 0:
                print(f"\n✅ 成功！会话已结束")
                
                # 3. 再次查询确认
                print(f"\n📊 步骤3: 确认状态变更")
                print("─" * 70)
                
                await asyncio.sleep(1)
                
                response = await client.post(
                    state_url,
                    params={"access_token": token, "debug": 1},
                    json=state_data
                )
                verify_result = response.json()
                
                if verify_result.get('errcode') == 0:
                    new_state = verify_result.get('service_state', -1)
                    new_state_name = state_map.get(new_state, "未知")
                    print(f"✅ 当前状态: {new_state_name} (state={new_state})")
                    
                    if new_state == 4:
                        print(f"\n🎉 完美！会话已成功结束")
                    else:
                        print(f"\n⚠️  状态变更可能未生效")
                
                # 4. 说明下一步
                print(f"\n{'=' * 70}")
                print("📝 下一步操作")
                print("=" * 70)
                print(f"\n会话已结束，现在用户重新发送消息会创建新会话。")
                print(f"\n⚠️  重要提示：")
                print(f"   新会话的初始状态仍由企业微信后台配置决定！")
                print(f"\n如果后台配置是「人工接待优先」：")
                print(f"   → 新会话仍会进入 state=3 ❌")
                print(f"\n如果后台配置是「智能助手接待」：")
                print(f"   → 新会话会进入 state=1 ✅")
                print(f"\n🔧 建议：")
                print(f"   1. 先修改企业微信后台配置为「仅智能助手接待」")
                print(f"   2. 然后在微信中重新发送消息")
                print(f"   3. 查看日志确认新会话状态")
                print(f"\n监控命令：")
                print(f"   tail -f logs/app_*.log | grep '会话状态'")
                
            else:
                errcode = trans_result.get('errcode')
                errmsg = trans_result.get('errmsg')
                print(f"\n❌ 结束会话失败")
                print(f"   错误码: {errcode}")
                print(f"   错误信息: {errmsg}")
                
                # 分析错误原因
                if errcode == 95016:
                    print(f"\n💡 分析: 95016 = 不允许的状态转换")
                    print(f"   可能原因:")
                    print(f"   - 从 state={service_state} 不能直接转到 state=4")
                    print(f"   - 需要接待人员权限")
                    print(f"   - 或者需要先转到其他状态")
                elif errcode == 95014:
                    print(f"\n💡 分析: 95014 = 用户不是接待人员")
                    print(f"   需要使用接待人员的凭证")
                elif errcode == 95001:
                    print(f"\n💡 分析: 95001 = 参数错误")
                    print(f"   检查 open_kfid 和 external_userid 是否正确")
                
                print(f"\n🔄 替代方案:")
                print(f"   1. 直接修改企业微信后台配置")
                print(f"   2. 用户删除/退出客服会话")
                print(f"   3. 重新进入发送消息")
                
                return False
            
            print("=" * 70)
            return True
            
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(end_session())
    sys.exit(0 if result else 1)

