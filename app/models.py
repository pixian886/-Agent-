"""SQLAlchemy 数据模型。"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now_iso() -> str:
    """返回秒级 ISO 时间字符串，统一写入数据库。"""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Base(DeclarativeBase):
    """所有模型的基类。"""


class User(Base):
    """学习者账号。"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[str] = mapped_column(
        String(32), nullable=False, default=utc_now_iso
    )

    lesson_progress: Mapped[list["LessonProgress"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    exercise_progress: Mapped[list["ExerciseProgress"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class LessonProgress(Base):
    """用户对某一课时的完成状态。没有记录视为未开始。"""

    __tablename__ = "lesson_progress"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "lesson_id",
            name="uq_lesson_progress_user_lesson",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lesson_id: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="completed"
    )
    updated_at: Mapped[str] = mapped_column(
        String(32), nullable=False, default=utc_now_iso
    )

    user: Mapped[User] = relationship(back_populates="lesson_progress")


class ExerciseProgress(Base):
    """用户对某一道练习的最新状态与提交次数。"""

    __tablename__ = "exercise_progress"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "exercise_id",
            name="uq_exercise_progress_user_exercise",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exercise_id: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 最新一次作答内容：选项索引、填空答案或代码，刷新后可恢复。
    last_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[str] = mapped_column(
        String(32), nullable=False, default=utc_now_iso
    )

    user: Mapped[User] = relationship(back_populates="exercise_progress")
