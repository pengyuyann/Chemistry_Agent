'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/15 17:47
@Author  : JunYU
@File    : main
'''

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置代理
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["https_proxy"] = "http://127.0.0.1:7897"

# 导入路由
from app.api.endpoints import chemagent_chat

# 创建FastAPI应用
app = FastAPI(
    title="Chemistry Agent API",
    description="智能化学助手API，支持分子分析、合成规划、安全性检查等化学任务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 添加CORS中间件，允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(
    chemagent_chat.router, 
    prefix="/api/chemagent", 
    tags=["Chemistry Agent"]
)

@app.get("/", tags=["Root"])
def read_root():
    """API根路径，返回基本信息"""
    return {
        "message": "Chemistry Agent API",
        "version": "1.0.0",
        "author": "Jun YU",
        "description": "智能化学助手API服务",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "chemagent": "/api/chemagent"
        }
    }

@app.get("/health", tags=["Health"])
def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "Chemistry Agent API",
        "version": "1.0.0"
    }

@app.get("/api/info", tags=["API Info"])
def get_api_info():
    """获取API详细信息"""
    return {
        "name": "Chemistry Agent API",
        "version": "1.0.0",
        "description": "智能化学助手API，基于大语言模型和化学工具链",
        "features": [
            "分子分析和计算",
            "化学反应预测",
            "合成路线规划",
            "安全性评估",
            "文献和专利搜索",
            "化学结构转换"
        ],
        "supported_models": [
            "deepseek-chat"
            "gpt-4-0613",
            "gpt-3.5-turbo-0613"
        ],
        "endpoints": {
            "chat": "/api/chemagent/",
            "health": "/api/chemagent/health",
            "tools": "/api/chemagent/tools"
        }
    }

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """处理404错误"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "请求的端点不存在",
            "available_endpoints": [
                "/",
                "/health",
                "/docs",
                "/api/info",
                "/api/chemagent/"
            ]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """处理500错误"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "服务器内部错误，请稍后重试"
        }
    )

if __name__ == "__main__":
    # 从环境变量获取配置
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("RELOAD", "True").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")
    
    print(f"🚀 启动 Chemistry Agent API 服务...")
    print(f"📍 服务地址: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    print(f"🔍 健康检查: http://{host}:{port}/health")
    print(f"🔄 热重载: {'启用' if reload else '禁用'}")
    print(f"📝 日志级别: {log_level}")
    
    # 启动服务器
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        reload=reload,
        log_level=log_level
    )