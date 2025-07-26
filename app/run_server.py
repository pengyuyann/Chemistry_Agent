#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Chemistry Agent 后端启动脚本
@Time    : 2025/1/27
@Author  : JunYU
@File    : run_server.py
"""

import os
import sys
import uvicorn
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置代理
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["https_proxy"] = "http://127.0.0.1:7897"

def load_environment():
    """加载环境变量"""
    # 尝试加载.env文件
    env_files = [
        project_root / ".env",
        project_root / "env_config.env",
        Path(".env")
    ]
    
    for env_file in env_files:
        if env_file.exists():
            load_dotenv(env_file)
            print(f"✅ 已加载环境变量文件: {env_file}")
            break

def ensure_database_tables():
    """确保数据库表存在"""
    try:
        from app.core.db.database import engine
        from app.core.db.models import Base
        
        # 创建数据库表（如果不存在）
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表检查完成")
        return True
    except Exception as e:
        print(f"⚠️  数据库表创建失败: {e}")
        return False

def create_app():
    """创建FastAPI应用"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from app.api.endpoints import chemagent_chat, auth, admin
    
    # 创建FastAPI应用
    app = FastAPI(
        title="Chemistry Agent API",
        description="智能化学助手API，支持分子分析、合成规划、安全性检查等化学任务",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
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
    app.include_router(
        auth.router,
        prefix="/api/auth",
        tags=["Auth"]
    )
    app.include_router(
        admin.router,
        prefix="/api/admin",
        tags=["Admin"]
    )
    
    # 根路径
    @app.get("/", tags=["Root"])
    def read_root():
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
    
    # 健康检查
    @app.get("/health", tags=["Health"])
    def health_check():
        return {
            "status": "healthy",
            "service": "Chemistry Agent API",
            "version": "1.0.0"
        }
    
    return app

def print_startup_info(host: str, port: int, reload: bool, log_level: str):
    """打印启动信息"""
    print("\n" + "="*60)
    print("🚀 Chemistry Agent API 服务启动")
    print("="*60)
    print(f"📍 服务地址: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    print(f"📖 ReDoc文档: http://{host}:{port}/redoc")
    print(f"🔍 健康检查: http://{host}:{port}/health")
    print(f"🔄 热重载: {'启用' if reload else '禁用'}")
    print(f"📝 日志级别: {log_level}")
    print("="*60)
    print("按 Ctrl+C 停止服务")
    print("="*60 + "\n")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Chemistry Agent API 启动脚本")
    parser.add_argument("--host", default=None, help="服务器主机地址")
    parser.add_argument("--port", type=int, default=None, help="服务器端口")
    parser.add_argument("--reload", action="store_true", help="启用热重载")
    parser.add_argument("--no-reload", action="store_true", help="禁用热重载")
    parser.add_argument("--log-level", default=None, help="日志级别")
    
    args = parser.parse_args()
    
    # 加载环境变量
    load_environment()
    
    # 确保数据库表存在
    ensure_database_tables()
    
    # 获取配置
    host = args.host or os.getenv("HOST", "0.0.0.0")
    port = args.port or int(os.getenv("PORT", 8000))
    
    # 处理reload参数
    if args.reload:
        reload = True
    elif args.no_reload:
        reload = False
    else:
        reload = os.getenv("RELOAD", "True").lower() == "true"
    
    log_level = args.log_level or os.getenv("LOG_LEVEL", "info")
    
    # 创建应用
    app = create_app()
    
    # 打印启动信息
    print_startup_info(host, port, reload, log_level)
    
    # 启动服务器
    try:
        if reload:
            # 当启用reload时，使用应用导入字符串
            uvicorn.run(
                "run_server:create_app",
                host=host,
                port=port,
                reload=reload,
                log_level=log_level,
                access_log=True,
                factory=True
            )
        else:
            # 当禁用reload时，直接传递应用实例
            uvicorn.run(
                app,
                host=host,
                port=port,
                reload=reload,
                log_level=log_level,
                access_log=True
            )
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()