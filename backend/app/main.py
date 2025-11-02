"""FastAPI 應用程式入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import simulation, websocket

# 建立 FastAPI 應用程式
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="CFD 求解器 Web API - 使用 SIMPLEC 演算法求解蓋驅動方腔流",
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(
    simulation.router,
    prefix=f"{settings.API_V1_PREFIX}/simulations",
    tags=["simulations"],
)

# 註冊 WebSocket 路由
app.include_router(
    websocket.router,
    prefix="/ws",
    tags=["websocket"],
)


@app.get("/")
async def root():
    """根端點"""
    return {
        "message": "CFD 求解器 API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "ok"}
