"""演示数据初始化。"""

from __future__ import annotations

from sqlalchemy import select

from app.auth import hash_password
from app.db import session_scope
from app.models import User

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo123"


def ensure_demo_user() -> None:
    """首次启动时写入演示账号，已存在则跳过。"""
    with session_scope() as db:
        exists = db.scalar(select(User.id).where(User.username == DEMO_USERNAME))
        if exists is not None:
            return

        db.add(
            User(
                username=DEMO_USERNAME,
                password_hash=hash_password(DEMO_PASSWORD),
            )
        )
