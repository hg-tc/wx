"""企业微信回调路由"""
from typing import Dict, Any
from fastapi import APIRouter, Request, Query, Depends, BackgroundTasks
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.wecom.auth import verify_url_signature
from app.wecom.webhook import WeComWebhook
from app.wecom.client import WeComClient
from app.wecom.kf_client import KfClient
from app.wecom.message_builder import MessageBuilder
from app.ai_engine.intent_classifier import IntentClassifier
from app.ai_engine.entity_extractor import EntityExtractor
from app.ai_engine.dialogue_manager import DialogueManager
from app.service_broker.service_manager import ServiceManager
from app.service_broker.matcher import ServiceMatcher
from app.service_broker.notification import MatchNotification
from app.tasks.crawler_tasks import crawl_products
from app.tasks.matcher_tasks import match_service
from app.utils.logger import get_logger

logger = get_logger()
router = APIRouter()

webhook = WeComWebhook()
wecom_client = WeComClient()
kf_client = KfClient()
message_builder = MessageBuilder()
intent_classifier = IntentClassifier()
entity_extractor = EntityExtractor()
dialogue_manager = DialogueManager()


@router.get("/callback", response_class=PlainTextResponse)
async def verify_callback(
    msg_signature: str = Query(...),
    timestamp: str = Query(...),
    nonce: str = Query(...),
    echostr: str = Query(...)
):
    """验证企业微信回调URL"""
    # 立即记录请求到达
    logger.info(f"🔔 收到回调验证请求 - signature={msg_signature[:20]}..., timestamp={timestamp}, nonce={nonce[:10]}...")
    try:
        result = verify_url_signature(msg_signature, timestamp, nonce, echostr)
        if result:
            logger.info(f"✅ 企业微信回调URL验证成功，返回: {result}")
            return PlainTextResponse(content=result, status_code=200)
        else:
            logger.error("❌ 企业微信回调URL验证失败")
            return PlainTextResponse(content="verification failed", status_code=400)
    except Exception as e:
        logger.error(f"❌ 验证回调URL失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return PlainTextResponse(content="error", status_code=500)


@router.post("/callback")
async def handle_callback(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    msg_signature: str = Query(...),
    timestamp: str = Query(...),
    nonce: str = Query(...)
):
    """处理企业微信消息回调"""
    try:
        # 获取请求体
        body = await request.body()
        
        # 解析消息
        message = webhook.parse_message(msg_signature, timestamp, nonce, body.decode())
        
        if not message:
            return "fail"
        
        # 🔥 检查是否为客服消息
        if webhook.is_kf_message(message):
            logger.info("🎯 检测到客服消息事件，开始处理...")
            kf_event = webhook.extract_kf_event(message)
            
            if kf_event:
                # 异步处理客服消息
                background_tasks.add_task(
                    process_kf_message,
                    db, kf_event
                )
            
            return "success"
        
        # 提取文本消息
        text_msg = webhook.extract_text_message(message)
        
        if text_msg:
            # 处理文本消息
            from_user = text_msg['from_user']
            content = text_msg['content']
            
            logger.info(f"收到消息: {from_user} -> {content}")
            
            # 异步处理消息
            background_tasks.add_task(
                process_user_message,
                db, from_user, content
            )
            
            return "success"
        
        # 处理事件消息
        event_msg = webhook.extract_event_message(message)
        if event_msg:
            logger.info(f"收到事件: {event_msg}")
            return "success"
        
        return "success"
        
    except Exception as e:
        logger.error(f"处理回调失败: {e}")
        return "fail"


async def process_user_message(db: AsyncSession, wecom_user_id: str, content: str):
    """处理用户消息"""
    try:
        # 获取或创建用户
        user = await get_or_create_user(db, wecom_user_id)
        if not user:
            await wecom_client.send_text_message(wecom_user_id, "系统错误，请稍后再试")
            return
        
        # 生成会话ID
        session_id = dialogue_manager.generate_session_id(str(user.id))
        
        # 保存用户消息
        await dialogue_manager.save_conversation(
            db, str(user.id), session_id, "user", content
        )
        
        # 识别意图
        intent = await intent_classifier.classify(content)
        logger.info(f"识别意图: {intent}")
        
        # 根据意图处理
        if intent == IntentClassifier.SUPPLY_SERVICE:
            await handle_supply_service(db, user, content, wecom_user_id)
        
        elif intent == IntentClassifier.DEMAND_SERVICE:
            await handle_demand_service(db, user, content, wecom_user_id)
        
        elif intent == IntentClassifier.SHOPPING_COMPARE:
            await handle_shopping(db, user, content, wecom_user_id)
        
        elif intent == IntentClassifier.QUERY_RECORDS:
            await handle_query_records(db, user, wecom_user_id)
        
        elif intent == IntentClassifier.HELP:
            help_msg = message_builder.build_help_message()
            await wecom_client.send_text_message(wecom_user_id, help_msg)
        
        else:
            # 闲聊
            response = await dialogue_manager.generate_contextualized_response(
                db, str(user.id), session_id, content
            )
            if response:
                await wecom_client.send_text_message(wecom_user_id, response)
                await dialogue_manager.save_conversation(
                    db, str(user.id), session_id, "assistant", response
                )
        
    except Exception as e:
        logger.error(f"处理用户消息失败: {e}")
        await wecom_client.send_text_message(wecom_user_id, "处理失败，请稍后再试")


async def process_kf_message(db: AsyncSession, kf_event: Dict[str, Any]):
    """处理客服消息"""
    try:
        token = kf_event['token']
        open_kfid = kf_event['open_kfid']
        
        logger.info(f"📨 处理客服消息 - OpenKfId: {open_kfid}, Token: {token[:20]}...")
        
        # 同步获取消息详情
        msg_data = await kf_client.sync_message(open_kfid, token)
        msg_list = msg_data.get('msg_list', [])
        
        # 只处理最新的一条消息（避免重复处理历史消息）
        if len(msg_list) > 1:
            logger.info(f"📬 收到 {len(msg_list)} 条消息，只处理最新的一条")
            msg_list = [msg_list[-1]]  # 取最后一条（最新的）
        
        if not msg_list:
            logger.warning("⚠️  未获取到任何客服消息")
            return
        
        logger.info(f"📬 获取到 {len(msg_list)} 条客服消息")
        
        # 处理每条消息
        for msg in msg_list:
            try:
                external_userid = msg.get('external_userid')
                msg_type = msg.get('msgtype')
                origin = msg.get('origin')  # 消息来源：3=客户发送
                msgid = msg.get('msgid')  # 消息ID
                
                logger.info(f"📝 处理客服消息 - 用户: {external_userid}, 类型: {msg_type}, 来源: {origin}, msgid: {msgid}")
                logger.info(f"🔍 完整消息内容: {msg}")
                
                # 处理文本消息
                if msg_type == 'text':
                    content = msg.get('text', {}).get('content', '')
                    
                    if content:
                        logger.info(f"💬 客服消息内容: {content}")
                        
                        # 检查会话状态（仅查询，不修改）
                        state_result = await kf_client.get_service_state(open_kfid, external_userid)
                        service_state = state_result.get('service_state', -1) if state_result.get('errcode') == 0 else -1
                        
                        # 企业微信官方文档: https://developer.work.weixin.qq.com/document/path/94669
                        # service_state定义:
                        # 0 = 新接入待处理（未分配）
                        # 1 = 由智能助手接待
                        # 2 = 待接入池排队中（不可发送消息）
                        # 3 = 由人工接待中（有servicer_userid）
                        # 4 = 已结束/已关闭
                        state_name = {
                            0: "新接入待处理", 
                            1: "智能助手接待", 
                            2: "待接入池排队", 
                            3: "人工接待中", 
                            4: "已结束",
                            -1: "未知"
                        }.get(service_state, "未知")
                        
                        servicer = state_result.get('servicer_userid', '')
                        if servicer:
                            logger.info(f"📊 当前会话状态: {state_name} (state={service_state}) | 接待人: {servicer}")
                        else:
                            logger.info(f"📊 当前会话状态: {state_name} (state={service_state})")
                        
                        # 检查是否可以发送消息
                        can_send = service_state in [0, 1, 3]  # 0待处理、1智能助手、3人工 都可以发送
                        if service_state == 2:
                            logger.warning(f"⚠️  会话在待接入池排队中，无法发送消息")
                            logger.warning(f"⚠️  解决方法：确保有接待人员或启用智能助手")
                            continue  # 跳过此消息
                        elif service_state == 4:
                            logger.warning(f"⚠️  会话已结束，无法发送消息")
                            continue  # 跳过此消息
                        
                        # 获取或创建外部用户
                        user = await get_or_create_external_user(db, external_userid)
                        
                        if not user:
                            logger.error(f"❌ 创建用户失败")
                            continue
                        
                        # 生成AI响应
                        response = await generate_ai_response(db, user, content)
                        logger.info(f"🤖 AI响应: {response[:50]}...")
                        
                        # 发送客服消息
                        send_result = await kf_client.send_text_message(
                            open_kfid,
                            external_userid,
                            response
                        )
                        
                        if send_result.get('errcode') == 0:
                            logger.info(f"✅ 成功发送客服消息")
                        else:
                            logger.error(f"❌ 发送失败: {send_result}")
                
                # 处理其他类型消息
                elif msg_type == 'image':
                    await kf_client.send_text_message(
                        open_kfid, external_userid, "收到您的图片，目前仅支持文字消息哦"
                    )
                
                elif msg_type == 'event':
                    event_type = msg.get('event', {}).get('event_type')
                    logger.info(f"📢 客服事件: {event_type}")
                    
                    # 处理进入会话事件
                    if event_type == 'enter_session':
                        await kf_client.send_text_message(
                            open_kfid,
                            external_userid,
                            "您好！我是智能助手，很高兴为您服务！\n\n我可以帮您：\n1️⃣ 发布或寻找服务\n2️⃣ 比价购物\n3️⃣ 查询历史记录\n\n请直接告诉我您需要什么吧！"
                        )
                
            except Exception as e:
                logger.error(f"处理单条客服消息失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
    except Exception as e:
        logger.error(f"处理客服消息失败: {e}")
        import traceback
        logger.error(traceback.format_exc())


async def get_or_create_user(db: AsyncSession, wecom_user_id: str) -> User:
    """获取或创建内部用户（普通应用）"""
    try:
        stmt = select(User).where(User.wecom_user_id == wecom_user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            # 创建新用户
            user = User(wecom_user_id=wecom_user_id, user_type="internal")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"创建新内部用户: {wecom_user_id}")
        
        return user
        
    except Exception as e:
        logger.error(f"获取或创建用户失败: {e}")
        return None


async def get_or_create_external_user(db: AsyncSession, external_userid: str) -> User:
    """获取或创建外部用户（客服应用）"""
    try:
        stmt = select(User).where(User.external_userid == external_userid)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            # 创建新外部用户
            user = User(external_userid=external_userid, user_type="external")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"创建新外部用户: {external_userid}")
        
        return user
        
    except Exception as e:
        logger.error(f"获取或创建外部用户失败: {e}")
        return None


async def generate_ai_response(db: AsyncSession, user: User, content: str) -> str:
    """生成AI响应（通用函数，支持内部和外部用户）
    
    Args:
        db: 数据库会话
        user: 用户对象
        content: 用户输入内容
        
    Returns:
        AI响应文本
    """
    try:
        # 生成会话ID
        session_id = dialogue_manager.generate_session_id(str(user.id))
        
        # 保存用户消息
        await dialogue_manager.save_conversation(
            db, str(user.id), session_id, "user", content
        )
        
        # 识别意图
        intent = await intent_classifier.classify(content)
        logger.info(f"🎯 识别意图: {intent}")
        
        response = ""
        
        # 根据意图生成响应
        if intent == IntentClassifier.SUPPLY_SERVICE:
            response = "好的！我帮您登记供应服务。\n\n请告诉我：\n1. 服务名称\n2. 服务描述\n3. 价格范围\n\n例如：「我提供Python编程培训，包含基础和进阶课程，价格3000-5000元」"
        
        elif intent == IntentClassifier.DEMAND_SERVICE:
            response = "好的！我帮您寻找服务。\n\n请告诉我：\n1. 需要什么服务\n2. 具体要求\n3. 预算范围\n\n例如：「我需要学习Python编程，想找个一对一的老师，预算5000元以内」"
        
        elif intent == IntentClassifier.SHOPPING_COMPARE:
            # 提取商品关键词
            entities = await entity_extractor.extract_shopping_entities(content)
            query = entities.get('query', content)
            response = f"正在为您搜索「{query}」的价格信息...\n\n稍后将为您推送最优惠的购买链接！"
            
            # 异步触发爬虫任务
            crawl_products.delay(query, str(user.id))
        
        elif intent == IntentClassifier.HELP:
            response = message_builder.build_help_message()
        
        else:
            # 闲聊或其他情况
            response = await dialogue_manager.generate_contextualized_response(
                db, str(user.id), session_id, content
            )
        
        # 保存AI响应
        if response:
            await dialogue_manager.save_conversation(
                db, str(user.id), session_id, "assistant", response
            )
        
        return response or "抱歉，我没有理解您的意思，请换个方式表达～"
        
    except Exception as e:
        logger.error(f"生成AI响应失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return "抱歉，系统出现了一点问题，请稍后再试～"


async def handle_supply_service(db: AsyncSession, user: User, content: str, wecom_user_id: str):
    """处理服务供应"""
    try:
        # 提取实体
        entities = await entity_extractor.extract_service_entities(content, "supply_service")
        
        # 创建服务
        manager = ServiceManager()
        service = await manager.create_service(db, str(user.id), "supply", entities)
        
        if service:
            # 通知用户
            notification = MatchNotification()
            await notification.notify_service_recorded(wecom_user_id, "supply", service.title)
            
            # 异步查找匹配
            match_service.delay(str(service.id))
        else:
            await wecom_client.send_text_message(wecom_user_id, "录入失败，请稍后再试")
    
    except Exception as e:
        logger.error(f"处理服务供应失败: {e}")
        await wecom_client.send_text_message(wecom_user_id, "处理失败，请稍后再试")


async def handle_demand_service(db: AsyncSession, user: User, content: str, wecom_user_id: str):
    """处理服务需求"""
    try:
        # 提取实体
        entities = await entity_extractor.extract_service_entities(content, "demand_service")
        
        # 创建服务
        manager = ServiceManager()
        service = await manager.create_service(db, str(user.id), "demand", entities)
        
        if service:
            # 通知用户
            notification = MatchNotification()
            await notification.notify_service_recorded(wecom_user_id, "demand", service.title)
            
            # 异步查找匹配
            match_service.delay(str(service.id))
        else:
            await wecom_client.send_text_message(wecom_user_id, "录入失败，请稍后再试")
    
    except Exception as e:
        logger.error(f"处理服务需求失败: {e}")
        await wecom_client.send_text_message(wecom_user_id, "处理失败，请稍后再试")


async def handle_shopping(db: AsyncSession, user: User, content: str, wecom_user_id: str):
    """处理购物比价"""
    try:
        # 提取购物实体
        entities = await entity_extractor.extract_shopping_entities(content)
        query = entities.get('query', content)
        
        # 发送等待消息
        await wecom_client.send_text_message(wecom_user_id, f"正在为您搜索「{query}」，请稍候...")
        
        # 异步爬取
        task = crawl_products.delay(query, str(user.id))
        
        # 这里简化处理，实际应该等待任务完成后再发送结果
        # 或者使用webhook通知用户
        await wecom_client.send_text_message(
            wecom_user_id,
            "搜索任务已提交，结果将在1-2分钟内发送给您"
        )
        
    except Exception as e:
        logger.error(f"处理购物比价失败: {e}")
        await wecom_client.send_text_message(wecom_user_id, "搜索失败，请稍后再试")


async def handle_query_records(db: AsyncSession, user: User, wecom_user_id: str):
    """处理查询记录"""
    try:
        manager = ServiceManager()
        services = await manager.get_user_services(db, str(user.id), limit=10)
        
        if not services:
            await wecom_client.send_text_message(wecom_user_id, "您还没有任何服务记录")
            return
        
        message = "📋 您的服务记录：\n\n"
        for idx, service in enumerate(services, 1):
            type_name = "供应" if service.type.value == "supply" else "需求"
            status_name = {"active": "活跃", "matched": "已匹配", "closed": "已关闭"}.get(service.status.value, "未知")
            
            message += f"{idx}. 【{type_name}】{service.title}\n"
            message += f"   状态：{status_name}\n"
            message += f"   创建时间：{service.created_at.strftime('%Y-%m-%d')}\n\n"
        
        await wecom_client.send_text_message(wecom_user_id, message)
        
    except Exception as e:
        logger.error(f"查询记录失败: {e}")
        await wecom_client.send_text_message(wecom_user_id, "查询失败，请稍后再试")

