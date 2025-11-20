"""FastAPI主应用"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.utils.logger import get_logger
from app.api.v1 import wecom, services, shopping, admin
import time

settings = get_settings()
logger = get_logger()

# 创建FastAPI应用
app = FastAPI(
    title="企业微信智能客服中介系统",
    description="基于DeepSeek大模型的智能客服中介系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 请求追踪中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有HTTP请求"""
    start_time = time.time()
    
    # 记录请求到达
    logger.info(f"📥 请求到达: {request.method} {request.url.path} | 来源: {request.client.host if request.client else 'unknown'}")
    
    # 如果是回调请求，记录详细信息
    if "callback" in request.url.path:
        logger.info(f"🔔 企业微信回调请求! 完整URL: {request.url}")
        logger.info(f"   查询参数: {dict(request.query_params)}")
    
    # 处理请求
    response = await call_next(request)
    
    # 记录响应
    process_time = time.time() - start_time
    logger.info(f"📤 响应: {request.method} {request.url.path} | 状态码: {response.status_code} | 耗时: {process_time:.3f}s")
    
    return response

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(wecom.router, prefix="/api/v1/wecom", tags=["企业微信"])
app.include_router(services.router, prefix="/api/v1/services", tags=["服务管理"])
app.include_router(shopping.router, prefix="/api/v1/shopping", tags=["购物比价"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["管理后台"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "企业微信智能客服中介系统",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("应用启动")
    logger.info(f"环境: {settings.APP_ENV}")
    logger.info(f"调试模式: {settings.APP_DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("应用关闭")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG
    )

