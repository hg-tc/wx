"""日志配置"""
import sys
from pathlib import Path
from loguru import logger
from app.config import get_settings

settings = get_settings()

# 创建日志目录
log_dir = Path("/opt/wecom-agent/logs") if settings.APP_ENV == "production" else Path("logs")
log_dir.mkdir(parents=True, exist_ok=True)

# 移除默认handler
logger.remove()

# 控制台输出
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.APP_LOG_LEVEL,
    colorize=True,
)

# 文件输出 - 普通日志
logger.add(
    log_dir / "app_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    encoding="utf-8",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)

# 文件输出 - 错误日志
logger.add(
    log_dir / "error_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="60 days",
    encoding="utf-8",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
)


def get_logger():
    """获取logger实例"""
    return logger

