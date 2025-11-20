"""企业微信消息构建器"""
from typing import List, Dict, Any


class MessageBuilder:
    """消息构建器"""
    
    @staticmethod
    def build_text_message(content: str) -> str:
        """构建文本消息"""
        return content
    
    @staticmethod
    def build_markdown_message(title: str, content: str) -> str:
        """构建Markdown消息"""
        return f"# {title}\n\n{content}"
    
    @staticmethod
    def build_service_match_message(matches: List[Dict[str, Any]]) -> str:
        """构建服务匹配结果消息"""
        if not matches:
            return "暂未找到匹配的服务，我们会继续为您寻找。"
        
        message = "🎯 为您找到以下匹配的服务：\n\n"
        for idx, match in enumerate(matches[:5], 1):  # 最多显示5个
            service = match.get('service', {})
            score = match.get('similarity_score', 0)
            
            message += f"**{idx}. {service.get('title', '未命名服务')}**\n"
            message += f"📝 描述：{service.get('description', '暂无描述')}\n"
            message += f"💰 价格：{service.get('price_range', '面议')}\n"
            message += f"📊 匹配度：{score * 100:.1f}%\n"
            message += f"🏷️ 标签：{', '.join(service.get('tags', []))}\n"
            message += "\n"
        
        message += "回复序号查看详细联系方式"
        return message
    
    @staticmethod
    def build_product_comparison_message(products: List[Dict[str, Any]]) -> str:
        """构建商品比价消息"""
        if not products:
            return "抱歉，暂未找到相关商品。"
        
        message = "🛒 商品比价结果：\n\n"
        
        # 找出最优惠的
        best_product = min(products, key=lambda x: x.get('final_price', float('inf')))
        
        for idx, product in enumerate(products[:5], 1):
            is_best = product == best_product
            prefix = "⭐ " if is_best else f"{idx}. "
            
            message += f"{prefix}**{product.get('title', '未知商品')}**\n"
            message += f"🏪 平台：{product.get('platform', '未知')}\n"
            message += f"💵 价格：¥{product.get('price', 0)}"
            
            if product.get('coupon', 0) > 0:
                message += f"（优惠券：¥{product.get('coupon')}）"
            
            message += f"\n💰 到手价：**¥{product.get('final_price', 0)}**"
            
            if is_best:
                message += " 🏆 最优惠"
            
            message += f"\n🔗 [查看详情]({product.get('url', '#')})\n"
            
            if product.get('seller_rating'):
                message += f"⭐ 商家评分：{product.get('seller_rating')}\n"
            
            message += "\n"
        
        return message
    
    @staticmethod
    def build_service_recorded_message(service_type: str, title: str) -> str:
        """构建服务录入成功消息"""
        type_name = "供应" if service_type == "supply" else "需求"
        return f"✅ 您的{type_name}服务已成功录入\n\n" \
               f"📋 标题：{title}\n\n" \
               f"我们会自动为您匹配合适的{'需求方' if service_type == 'supply' else '供应方'}，" \
               f"一旦有匹配结果会立即通知您。"
    
    @staticmethod
    def build_error_message(error: str = "处理失败") -> str:
        """构建错误消息"""
        return f"❌ {error}\n\n如需帮助，请联系管理员。"
    
    @staticmethod
    def build_help_message() -> str:
        """构建帮助消息"""
        return """👋 欢迎使用智能客服中介系统！

我可以帮您：

**1️⃣ 服务中介**
• 发布供应服务：我可以提供XXX服务
• 发布需求服务：我需要XXX服务
• 自动智能匹配供需双方

**2️⃣ 商品比价**
• 搜索商品：帮我找XXX
• 多平台比价（淘宝、咸鱼、微信）
• 推荐最优惠链接

**3️⃣ 查询记录**
• 查看我的服务记录
• 查看匹配历史

直接发送您的需求即可开始！"""
    
    @staticmethod
    def build_news_articles(products: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """构建图文消息（用于商品展示）"""
        articles = []
        for product in products[:8]:  # 最多8条
            article = {
                "title": product.get('title', '未知商品'),
                "description": f"{product.get('platform', '未知')} - ¥{product.get('final_price', 0)}",
                "url": product.get('url', '#'),
                "picurl": product.get('image', '')
            }
            articles.append(article)
        return articles

