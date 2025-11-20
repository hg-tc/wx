"""向量化服务"""
import hashlib
from typing import List, Optional
from app.ai_engine.deepseek_client import DeepSeekClient
from app.utils.logger import get_logger

logger = get_logger()


class EmbeddingService:
    """向量化服务"""
    
    def __init__(self):
        self.client = DeepSeekClient()
        self.dimension = 1536  # 标准embedding维度
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """获取文本向量
        
        注意：这里需要配置实际的embedding服务
        DeepSeek可能不提供embedding endpoint，需要使用：
        1. OpenAI embedding API
        2. 开源模型如sentence-transformers
        3. 其他embedding服务
        """
        try:
            # 方案1：使用OpenAI embedding（推荐）
            # from openai import AsyncOpenAI
            # client = AsyncOpenAI(api_key="your-openai-key")
            # response = await client.embeddings.create(
            #     model="text-embedding-ada-002",
            #     input=text
            # )
            # return response.data[0].embedding
            
            # 方案2：使用本地模型（需要安装sentence-transformers）
            # from sentence_transformers import SentenceTransformer
            # model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            # embedding = model.encode(text)
            # return embedding.tolist()
            
            # 临时方案：使用简单的哈希向量（仅用于开发测试）
            logger.warning("使用临时哈希向量方案，生产环境请配置实际的embedding服务")
            return self._hash_to_vector(text)
            
        except Exception as e:
            logger.error(f"获取embedding失败: {e}")
            return None
    
    def _hash_to_vector(self, text: str) -> List[float]:
        """将文本哈希转换为向量（临时方案，仅用于开发）"""
        # 生成多个哈希值
        vector = []
        for i in range(self.dimension // 32):
            hash_obj = hashlib.sha256(f"{text}_{i}".encode())
            hash_bytes = hash_obj.digest()
            # 将字节转换为浮点数
            for j in range(0, len(hash_bytes), 4):
                if len(vector) >= self.dimension:
                    break
                chunk = hash_bytes[j:j+4]
                value = int.from_bytes(chunk, byteorder='big') / (2**32)
                vector.append(value - 0.5)  # 归一化到[-0.5, 0.5]
        
        # 补齐或截断到指定维度
        while len(vector) < self.dimension:
            vector.append(0.0)
        return vector[:self.dimension]
    
    async def get_batch_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """批量获取向量"""
        embeddings = []
        for text in texts:
            embedding = await self.get_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        import math
        
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

