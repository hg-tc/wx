"""Celery应用配置"""
from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

# 创建Celery应用
celery_app = Celery(
    "wecom_agent",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.crawler_tasks",
        "app.tasks.matcher_tasks",
    ]
)

# Celery配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5分钟超时
    task_soft_time_limit=240,  # 4分钟软超时
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# 定时任务配置
celery_app.conf.beat_schedule = {
    # 每小时批量匹配服务
    "batch-match-services": {
        "task": "app.tasks.matcher_tasks.batch_match_services",
        "schedule": crontab(minute=0),  # 每小时执行
    },
    # 每天清理过期服务
    "clean-expired-services": {
        "task": "app.tasks.matcher_tasks.clean_expired_services",
        "schedule": crontab(hour=2, minute=0),  # 每天凌晨2点执行
    },
    # 每6小时清理过期缓存
    "clean-expired-cache": {
        "task": "app.tasks.crawler_tasks.clean_expired_cache",
        "schedule": crontab(hour="*/6", minute=0),  # 每6小时执行
    },
}

