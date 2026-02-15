"""
EA Trading Backend - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes import credential_routes, exchange_routes, test_routes, follower_routes, auth_routes, user_routes, follow_config_routes, trade_routes, dashboard_routes, trader_routes, ea_routes

app = FastAPI(
    title="EA Trading Backend",
    description="自動化跟單系統後端 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - 允許前端跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React/Next.js 開發環境
        "http://localhost:5173",  # Vite 開發環境
        "http://localhost:8080",  # Vue 開發環境
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法
    allow_headers=["*"],  # 允許所有 Headers
    expose_headers=["*"],  # 暴露所有 Headers 給前端
)

# 註冊路由
app.include_router(auth_routes.router)  # 認證路由
app.include_router(user_routes.router)  # 用戶路由
app.include_router(dashboard_routes.router)  # 儀表板聚合路由 ✨
app.include_router(trader_routes.router)  # 交易員管理路由 ✨
app.include_router(ea_routes.router)  # EA 專用路由 ✨
app.include_router(follow_config_routes.router)  # 跟單配置路由
app.include_router(trade_routes.router)  # 交易歷史路由
app.include_router(credential_routes.router)
app.include_router(exchange_routes.router)
app.include_router(follower_routes.router)  # 跟單引擎路由
app.include_router(test_routes.router)  # 測試路由（開發用）


@app.get("/")
async def root():
    """健康檢查端點"""
    return {
        "status": "ok",
        "message": "EA Trading Backend API is running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
