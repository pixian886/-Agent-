"""项目路径与运行配置。"""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = BASE_DIR / "content"
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
STATIC_DIR = BASE_DIR / "app" / "static"

DB_PATH = DATA_DIR / "app.db"
SECRET_KEY_PATH = DATA_DIR / "secret_key"

# 默认只监听本机，避免在未知网络中暴露判题服务。
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# 部署模式：local 默认关闭 HTTPS 限制；production 默认启用 Secure Cookie。
APP_ENV = os.getenv("APP_ENV", "local").strip().lower()
HTTPS_ONLY = os.getenv(
    "HTTPS_ONLY", "true" if APP_ENV == "production" else "false"
).strip().lower() in {"1", "true", "yes", "on"}
TRUST_PROXY = os.getenv("TRUST_PROXY", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

# 判题模式：本地 subprocess；线上 docker；无法隔离时 disabled。
JUDGE_MODE = os.getenv("JUDGE_MODE", "subprocess").strip().lower()
if JUDGE_MODE not in {"subprocess", "docker", "disabled"}:
    raise RuntimeError("JUDGE_MODE 仅支持 subprocess / docker / disabled")

JUDGE_DOCKER_IMAGE = os.getenv("JUDGE_DOCKER_IMAGE", "plg-judge:latest").strip()
DOCKER_BIN = os.getenv("DOCKER_BIN", "docker").strip() or "docker"
JUDGE_CONCURRENCY = int(os.getenv("JUDGE_CONCURRENCY", "2"))
if not 1 <= JUDGE_CONCURRENCY <= 4:
    raise RuntimeError("JUDGE_CONCURRENCY 必须是 1~4 的整数")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


def ensure_data_dir() -> None:
    """确保数据目录存在。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def database_url() -> str:
    """返回数据库连接串；线上可用 DATABASE_URL 覆盖。"""
    if DATABASE_URL:
        return DATABASE_URL
    return f"sqlite:///{DB_PATH.as_posix()}"


def load_or_create_secret_key() -> str:
    """读取或生成会话签名密钥，保证重启后登录态不失效。"""
    ensure_data_dir()
    if SECRET_KEY_PATH.exists():
        key = SECRET_KEY_PATH.read_text(encoding="utf-8").strip()
        if key:
            return key

    key = os.urandom(32).hex()
    SECRET_KEY_PATH.write_text(key, encoding="utf-8")
    return key
