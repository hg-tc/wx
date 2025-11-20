"""安全相关工具函数"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings

settings = get_settings()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """验证JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_random_string(length: int = 32) -> str:
    """生成随机字符串"""
    return secrets.token_urlsafe(length)


def calculate_signature(data: str, secret: str) -> str:
    """计算签名"""
    return hashlib.sha256(f"{data}{secret}".encode()).hexdigest()


def encrypt_sensitive_data(data: str) -> str:
    """加密敏感数据（简单示例，生产环境应使用更强的加密）"""
    # TODO: 实现更强的加密算法（如AES）
    return hashlib.sha256(f"{data}{settings.SECRET_KEY}".encode()).hexdigest()


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """解密敏感数据"""
    # TODO: 实现对应的解密算法
    return encrypted_data

