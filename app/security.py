"""CSRF 校验、单进程限流与请求辅助。"""

from __future__ import annotations

import hmac
import secrets
import threading
import time
from collections import deque

from fastapi import Header, HTTPException, Request

from app.config import TRUST_PROXY

CSRF_SESSION_KEY = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"


def get_csrf_token(request: Request) -> str:
    """读取或生成当前会话的 CSRF Token。"""
    token = request.session.get(CSRF_SESSION_KEY)
    if not isinstance(token, str) or not token:
        token = secrets.token_urlsafe(32)
        request.session[CSRF_SESSION_KEY] = token
    return token


def validate_csrf(request: Request, token: str | None) -> None:
    """校验表单或请求头中的 CSRF Token；失败返回 403。"""
    expected = request.session.get(CSRF_SESSION_KEY)
    if not isinstance(expected, str) or not expected:
        raise HTTPException(status_code=403, detail="页面已过期，请刷新后重试")
    if not token or not hmac.compare_digest(expected, token):
        raise HTTPException(status_code=403, detail="页面已过期，请刷新后重试")


def require_csrf(
    request: Request,
    x_csrf_token: str | None = Header(default=None, alias=CSRF_HEADER_NAME),
) -> None:
    """FastAPI 依赖：JSON 接口通过 X-CSRF-Token 请求头校验。"""
    validate_csrf(request, x_csrf_token)


def client_ip(request: Request) -> str:
    """返回客户端 IP；线上由 Caddy 代理时可选择信任 X-Forwarded-For。"""
    if TRUST_PROXY:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimiter:
    """单进程内存限流：窗口内事件数达到上限即拒绝。"""

    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds

        with self._lock:
            events = self._events.setdefault(key, deque())
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= limit:
                return False
            events.append(now)
            return True

    def reset(self, key: str) -> None:
        with self._lock:
            self._events.pop(key, None)


rate_limiter = RateLimiter()

LOGIN_LIMIT = (5, 15 * 60)
REGISTER_LIMIT = (60, 60 * 60)
SUBMIT_LIMIT = (30, 60)
COMPLETE_LIMIT = (20, 60)
