"""对话管理器"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Conversation, MessageRole
from app.models.user import User
from app.ai_engine.deepseek_client import DeepSeekClient
from app.utils.logger import get_logger

logger = get_logger()


class DialogueManager:
    """对话管理器"""
    
    def __init__(self):
        self.client = DeepSeekClient()
        self.max_history = 10  # 最多保留的对话历史数量
        self.session_timeout = timedelta(hours=2)  # 会话超时时间
    
    async def get_conversation_history(
        self, 
        db: AsyncSession, 
        user_id: str, 
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """获取对话历史"""
        try:
            # 查询最近的对话
            cutoff_time = datetime.utcnow() - self.session_timeout
            
            stmt = select(Conversation).where(
                Conversation.user_id == user_id,
                Conversation.session_id == session_id,
                Conversation.created_at >= cutoff_time
            ).order_by(Conversation.created_at.desc()).limit(limit)
            
            result = await db.execute(stmt)
            conversations = result.scalars().all()
            
            # 转换为消息格式（倒序，最早的在前）
            messages = []
            for conv in reversed(conversations):
                messages.append({
                    "role": conv.role.value,
                    "content": conv.content
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
    
    async def save_conversation(
        self,
        db: AsyncSession,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
        intent: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None
    ) -> bool:
        """保存对话"""
        try:
            conversation = Conversation(
                user_id=user_id,
                session_id=session_id,
                role=MessageRole(role),
                content=content,
                intent=intent,
                entities=entities
            )
            
            db.add(conversation)
            await db.commit()
            logger.info(f"保存对话: user={user_id}, role={role}")
            return True
            
        except Exception as e:
            logger.error(f"保存对话失败: {e}")
            await db.rollback()
            return False
    
    async def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        system_prompt: str = "你是企业微信智能客服助手，友好、专业地回答用户问题。"
    ) -> Optional[str]:
        """生成回复"""
        try:
            # 构建消息列表
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加历史对话
            messages.extend(conversation_history[-self.max_history:])
            
            # 添加当前消息
            messages.append({"role": "user", "content": user_message})
            
            # 调用AI生成回复
            response = await self.client.chat_completion(messages)
            return response
            
        except Exception as e:
            logger.error(f"生成回复失败: {e}")
            return None
    
    async def generate_contextualized_response(
        self,
        db: AsyncSession,
        user_id: str,
        session_id: str,
        user_message: str,
        context: Optional[str] = None
    ) -> Optional[str]:
        """生成带上下文的回复"""
        try:
            # 获取历史对话
            history = await self.get_conversation_history(db, user_id, session_id)
            
            # 构建系统提示
            system_prompt = "你是企业微信智能客服助手，友好、专业地回答用户问题。"
            if context:
                system_prompt += f"\n\n当前上下文：{context}"
            
            # 生成回复
            response = await self.generate_response(user_message, history, system_prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"生成上下文回复失败: {e}")
            return None
    
    def generate_session_id(self, user_id: str) -> str:
        """生成会话ID"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H")
        return f"{user_id}_{timestamp}"

