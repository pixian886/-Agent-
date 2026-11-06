"""密码哈希、登录态与表单校验。"""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User

PBKDF2_PREFIX = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 200_000
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_\u4e00-\u9fff]{3,20}$")


class LoginRequiredError(Exception):
    """页面访问需要登录时抛出，由应用统一跳转到登录页。"""


def hash_password(password: str) -> str:
    """生成带随机盐的密码哈希，格式：算法$迭代次数$盐$哈希。"""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return f"{PBKDF2_PREFIX}${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """校验密码；格式错误时返回 False，不抛出异常。"""
    try:
        prefix, iterations_text, salt_hex, digest_hex = stored.split("$", 3)
        if prefix != PBKDF2_PREFIX:
            return False
        iterations = int(iterations_text)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (ValueError, TypeError):
        return False

    actual = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(actual, expected)


def is_valid_username(username: str) -> bool:
    """用户名允许中文、字母、数字和下划线，长度 3~20。"""
    return bool(USERNAME_PATTERN.fullmatch(username))


def is_valid_password(password: str) -> bool:
    """密码长度限制为 6~64 位。"""
    return 6 <= len(password) <= 64


def is_logged_in(request: Request) -> bool:
    """只检查 Session 中是否存在用户 ID，不查询数据库。"""
    return isinstance(request.session.get("user_id"), int)


def login_user(request: Request, user: User) -> None:
    """登录时清空旧会话，避免会话固定攻击。"""
    request.session.clear()
    request.session["user_id"] = user.id


def logout_user(request: Request) -> None:
    """清空当前会话。"""
    request.session.clear()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User | None:
    """从签名 Session 中读取用户；用户已不存在时清空会话。"""
    user_id = request.session.get("user_id")
    if not isinstance(user_id, int):
        return None

    user = db.get(User, user_id)
    if user is None:
        request.session.clear()
    return user


def require_user(
    user: User | None = Depends(get_current_user),
) -> User:
    """页面依赖：未登录时抛出异常，由 main.py 统一重定向。"""
    if user is None:
        raise LoginRequiredError()
    return user


def require_api_user(
    user: User | None = Depends(get_current_user),
) -> User:
    """API 依赖：未登录返回 401，而不是跳转登录页。"""
    if user is None:
        raise HTTPException(status_code=401, detail="请先登录")
    return user
