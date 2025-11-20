"""配置管理模块"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_ENV: str = "development"
    APP_DEBUG: bool = False
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_LOG_LEVEL: str = "INFO"
    
    # DeepSeek API配置
    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # 企业微信配置
    WECOM_CORP_ID: str
    WECOM_AGENT_ID: str
    WECOM_SECRET: str
    WECOM_TOKEN: str
    WECOM_ENCODING_AES_KEY: str
    
    # 企业微信客服配置
    WECOM_KF_ACCOUNT_ID: str = ""  # 客服账号ID (OpenKfId)
    WECOM_KF_SECRET: str = ""  # 客服应用Secret（用于获取客服专用access_token）
    
    # 数据库配置
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 淘宝联盟配置
    TAOBAO_APP_KEY: str = ""
    TAOBAO_APP_SECRET: str = ""
    
    # 拼多多配置
    PDD_CLIENT_ID: str = ""
    PDD_CLIENT_SECRET: str = ""
    
    # 爬虫配置
    CRAWLER_PROXY_POOL: str = ""
    CRAWLER_MAX_CONCURRENT: int = 5
    CRAWLER_TIMEOUT: int = 30
    CRAWLER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # 安全配置
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    
    # 向量配置
    EMBEDDING_DIMENSION: int = 1536
    
    # 缓存配置
    CACHE_EXPIRE_TIME: int = 3600
    PRODUCT_CACHE_EXPIRE: int = 7200
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()

