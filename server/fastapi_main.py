#!/usr/bin/env python3
"""
股票分析系统FastAPI后端
用于测试优化后的分析算法
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api import analysis, stocks, portfolio, military_rules
from app.database import Base

# 创建数据库引擎
SQLALCHEMY_DATABASE_URL = "sqlite:///./stock_analysis.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="股票分析系统API",
    description="优化后的股票分析算法API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(military_rules.router, prefix="/api/military-rules", tags=["military-rules"])

# 健康检查端点
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Stock Analysis FastAPI Backend is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
