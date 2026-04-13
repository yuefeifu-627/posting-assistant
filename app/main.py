"""FastAPI 应用入口"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import init_db
from app.logger import setup_logging, get_logger
from app.exceptions import AppException
from app.routers import posts, themes, auth, corpus_user
from app.dependencies import get_ai_service
from app.di import IAIService

# 初始化
settings = get_settings()
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("初始化数据库...")
    init_db()
    logger.info("应用启动完成")
    yield
    logger.info("应用关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    description="基于AI的用车总结文章生成工具",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置（允许 Streamlit 前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """应用异常处理"""
    logger.warning(f"业务异常: {exc.code} - {exc.message}")
    status_code = 404 if exc.code == "NOT_FOUND" else 400
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message, "code": exc.code}
    )


# 注册路由
app.include_router(themes.router)
app.include_router(posts.router)
app.include_router(auth.router)
app.include_router(corpus_user.router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用{settings.app_name}",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check(ai_service: IAIService = Depends(get_ai_service)):
    """健康检查"""
    ai_connected = ai_service.test_connection()
    models = ai_service.get_available_models() if ai_connected else []
    api_config = ai_service.check_api_config()
    provider_info = ai_service.get_provider_info()
    plugin_metadata = ai_service.get_plugin_metadata()

    return {
        "status": "healthy",
        "ai_connected": ai_connected,
        "available_models": models,
        "glm_configured": api_config["glm_configured"],
        "glm_model": api_config["glm_model"],
        "minmax_configured": api_config["minmax_configured"],
        "minmax_model": api_config["minmax_model"],
        "providers": provider_info,
        "plugins": plugin_metadata,
        "config": {
            "ollama_model": settings.ollama_model,
            "base_url": settings.ollama_base_url
        }
    }
