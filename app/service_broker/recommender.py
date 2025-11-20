"""服务推荐器"""
from typing import List, Dict, Any
from app.utils.logger import get_logger

logger = get_logger()


class ServiceRecommender:
    """服务推荐器"""
    
    def rank_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """对匹配结果进行排序"""
        # 已经在matcher中计算了comprehensive_score并排序
        # 这里可以添加额外的排序逻辑
        return matches
    
    def filter_matches(
        self,
        matches: List[Dict[str, Any]],
        min_score: float = 0.5,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """过滤匹配结果"""
        filtered = [m for m in matches if m.get('similarity_score', 0) >= min_score]
        return filtered[:max_results]
    
    def explain_match(self, match: Dict[str, Any]) -> str:
        """解释匹配原因"""
        score = match.get('similarity_score', 0)
        vector_sim = match.get('vector_similarity', 0)
        
        explanation = f"匹配度 {score * 100:.1f}%\n"
        
        if vector_sim >= 0.8:
            explanation += "• 高度语义相似\n"
        elif vector_sim >= 0.6:
            explanation += "• 较高语义相似\n"
        elif vector_sim >= 0.4:
            explanation += "• 中等语义相似\n"
        
        service = match.get('service', {})
        tags = service.get('tags', [])
        if tags:
            explanation += f"• 相关标签：{', '.join(tags[:3])}\n"
        
        return explanation

