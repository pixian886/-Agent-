"""FastAPI 应用入口。"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.auth import LoginRequiredError
from app.config import (
    APP_ENV,
    HTTPS_ONLY,
    STATIC_DIR,
    load_or_create_secret_key,
)
from app.content import init_course
from app.db import check_database, init_db
from app.routes.api import router as api_router
from app.routes.auth_routes import router as auth_router
from app.routes.pages import router as pages_router
from app.seed import ensure_demo_user

# 生产环境必须显式提供固定的会话密钥，避免重建容器后登录态全部失效。
if APP_ENV == "production" and not os.getenv("APP_SECRET_KEY"):
    raise RuntimeError("APP_ENV=production 时必须设置 APP_SECRET_KEY")

# 本地启动时仍然自动生成并持久化密钥。
os.environ.setdefault("APP_SECRET_KEY", load_or_create_secret_key())


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """启动时加载课程、建表并写入演示账号；重复执行是安全的。"""
    init_course()
    init_db()
    ensure_demo_user()
    yield


app = FastAPI(title="从零开始Agent学习", lifespan=lifespan)

# 签名 Cookie 保存登录态；HttpOnly 由 SessionMiddleware 默认开启。
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ["APP_SECRET_KEY"],
    session_cookie="plg_session",
    max_age=7 * 24 * 60 * 60,
    same_site="lax",
    https_only=HTTPS_ONLY,
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """给所有响应加基础安全头；线上启用 HSTS。"""
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault(
        "Referrer-Policy", "strict-origin-when-cross-origin"
    )
    response.headers.setdefault(
        "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
    )
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        "img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self'; "
        "font-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'",
    )
    if HTTPS_ONLY:
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains",
        )
    return response


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(auth_router)
app.include_router(api_router)
app.include_router(pages_router)


@app.exception_handler(LoginRequiredError)
async def login_required_handler(
    _request: Request, _exc: LoginRequiredError
) -> RedirectResponse:
    """未登录访问受保护页面时统一跳转登录页。"""
    return RedirectResponse("/login", status_code=303)


@app.get("/health")
def health() -> dict[str, str]:
    """健康检查：确认数据库可连接。"""
    check_database()
    return {"status": "ok", "database": "ok"}
