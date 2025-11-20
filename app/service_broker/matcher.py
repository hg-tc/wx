"""服务匹配引擎"""
from typing import List, Dict, Any, Optional
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.service import Service, ServiceType, ServiceStatus, Match, MatchStatus
from app.ai_engine.embedding_service import EmbeddingService
from app.utils.logger import get_logger

logger = get_logger()


class ServiceMatcher:
    """服务匹配引擎"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
    
    async def find_matches(
        self,
        db: AsyncSession,
        service: Service,
        top_k: int = 10,
        threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """为服务查找匹配项"""
        try:
            # 确定要查找的服务类型（供应找需求，需求找供应）
            target_type = ServiceType.DEMAND if service.type == ServiceType.SUPPLY else ServiceType.SUPPLY
            
            if not service.embedding:
                logger.warning(f"服务{service.id}没有embedding，无法匹配")
                return []
            
            # 使用pgvector进行向量相似度搜索
            # 注意：这里需要使用原始SQL，因为SQLAlchemy的pgvector支持有限
            query = text("""
                SELECT 
                    id,
                    user_id,
                    title,
                    description,
                    category,
                    price_range,
                    tags,
                    contact_info,
                    created_at,
                    1 - (embedding <=> :target_embedding) as similarity
                FROM services
                WHERE 
                    type = :target_type
                    AND status = 'active'
                    AND expired_at > NOW()
                    AND user_id != :user_id
                ORDER BY embedding <=> :target_embedding
                LIMIT :top_k
            """)
            
            result = await db.execute(
                query,
                {
                    "target_embedding": service.embedding,
                    "target_type": target_type.value,
                    "user_id": service.user_id,
                    "top_k": top_k
                }
            )
            
            matches = []
            for row in result:
                similarity = row.similarity
                
                # 应用阈值过滤
                if similarity < threshold:
                    continue
                
                # 计算综合评分
                total_score = self._calculate_comprehensive_score(
                    service, 
                    {
                        'id': row.id,
                        'title': row.title,
                        'description': row.description,
                        'category': row.category,
                        'price_range': row.price_range,
                        'tags': row.tags,
                        'created_at': row.created_at
                    },
                    similarity
                )
                
                matches.append({
                    'service_id': str(row.id),
                    'service': {
                        'id': str(row.id),
                        'user_id': str(row.user_id),
                        'title': row.title,
                        'description': row.description,
                        'category': row.category,
                        'price_range': row.price_range,
                        'tags': row.tags,
                        'contact_info': row.contact_info,
                        'created_at': row.created_at.isoformat() if row.created_at else None
                    },
                    'similarity_score': total_score,
                    'vector_similarity': similarity
                })
            
            # 按综合评分排序
            matches.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            logger.info(f"为服务{service.id}找到{len(matches)}个匹配")
            return matches
            
        except Exception as e:
            logger.error(f"查找匹配失败: {e}")
            return []
    
    def _calculate_comprehensive_score(
        self,
        source_service: Service,
        target_service: Dict[str, Any],
        vector_similarity: float
    ) -> float:
        """计算综合评分"""
        # 向量相似度权重
        score = 0.6 * vector_similarity
        
        # 关键词匹配权重
        keyword_match = self._calculate_keyword_match(
            source_service.tags or [],
            target_service.get('tags', []) or []
        )
        score += 0.2 * keyword_match
        
        # 分类匹配权重
        category_match = 1.0 if source_service.category == target_service.get('category') else 0.0
        score += 0.1 * category_match
        
        # 时间新鲜度权重（越新越好）
        from datetime import datetime, timezone
        if target_service.get('created_at'):
            days_old = (datetime.now(timezone.utc) - target_service['created_at']).days
            freshness = max(0, 1 - days_old / 30)  # 30天内线性衰减
        else:
            freshness = 0.5
        score += 0.1 * freshness
        
        return score
    
    def _calculate_keyword_match(self, tags1: List[str], tags2: List[str]) -> float:
        """计算关键词匹配度"""
        if not tags1 or not tags2:
            return 0.0
        
        set1 = set(tag.lower() for tag in tags1)
        set2 = set(tag.lower() for tag in tags2)
        
        if not set1 or not set2:
            return 0.0
        
        intersection = set1 & set2
        union = set1 | set2
        
        return len(intersection) / len(union)  # Jaccard相似度
    
    async def create_match_record(
        self,
        db: AsyncSession,
        supply_id: str,
        demand_id: str,
        similarity_score: float
    ) -> Optional[Match]:
        """创建匹配记录"""
        try:
            match = Match(
                supply_id=supply_id,
                demand_id=demand_id,
                similarity_score=similarity_score,
                status=MatchStatus.PENDING
            )
            
            db.add(match)
            await db.commit()
            await db.refresh(match)
            
            logger.info(f"创建匹配记录: supply={supply_id}, demand={demand_id}, score={similarity_score}")
            return match
            
        except Exception as e:
            logger.error(f"创建匹配记录失败: {e}")
            await db.rollback()
            return None
    
    async def update_match_status(
        self,
        db: AsyncSession,
        match_id: str,
        status: str
    ) -> bool:
        """更新匹配状态"""
        try:
            stmt = select(Match).where(Match.id == match_id)
            result = await db.execute(stmt)
            match = result.scalar_one_or_none()
            
            if not match:
                return False
            
            match.status = MatchStatus(status)
            await db.commit()
            
            logger.info(f"更新匹配状态: {match_id} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"更新匹配状态失败: {e}")
            await db.rollback()
            return False

