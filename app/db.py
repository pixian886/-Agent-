"""数据库引擎、会话与初始化。"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import DATA_DIR, database_url, ensure_data_dir
from app.models import Base

ensure_data_dir()

LESSON_ID_MIGRATION_MARKER = DATA_DIR / "lesson_id_v2.migrated"

engine = create_engine(
    database_url(),
    connect_args={"check_same_thread": False},
    future=True,
)


@event.listens_for(engine, "connect")
def _configure_sqlite(dbapi_connection, connection_record) -> None:
    """SQLite 连接级配置：外键、WAL 与写锁等待。"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def init_db() -> None:
    """创建全部表，并为已有数据库补齐新增列。"""
    Base.metadata.create_all(bind=engine)
    _ensure_exercise_progress_columns()
    _migrate_legacy_lesson_ids()


def _ensure_exercise_progress_columns() -> None:
    """轻量迁移：已有数据库缺少 last_answer 时补充该列。"""
    with engine.begin() as connection:
        columns = {
            row[1]
            for row in connection.exec_driver_sql(
                "PRAGMA table_info(exercise_progress)"
            )
        }
        if "last_answer" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE exercise_progress ADD COLUMN last_answer TEXT"
            )


def _migrate_legacy_lesson_ids() -> None:
    """一次性迁移：旧版 l07/l08 顺延为 l10/l11，避免旧进度误标新课时。"""
    if LESSON_ID_MIGRATION_MARKER.exists():
        return

    with engine.begin() as connection:
        connection.exec_driver_sql(
            "UPDATE lesson_progress SET lesson_id = 'l10' WHERE lesson_id = 'l07'"
        )
        connection.exec_driver_sql(
            "UPDATE lesson_progress SET lesson_id = 'l11' WHERE lesson_id = 'l08'"
        )

    LESSON_ID_MIGRATION_MARKER.write_text("ok", encoding="utf-8")


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖：每个请求使用独立 Session。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """脚本与初始化逻辑使用的事务上下文。"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_database() -> None:
    """执行一次最小查询，用于健康检查。"""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
