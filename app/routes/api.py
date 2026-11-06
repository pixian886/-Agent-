"""练习提交与判题接口。"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_api_user
from app.config import JUDGE_MODE
from app.content import Exercise, get_catalog
from app.db import get_db
from app.judge import JudgeResult, judge_choice, judge_coding, judge_fill
from app.models import ExerciseProgress, LessonProgress, User, utc_now_iso
from app.security import (
    COMPLETE_LIMIT,
    SUBMIT_LIMIT,
    rate_limiter,
    require_csrf,
)
from app.trajectory import MAX_JSON_BYTES, evaluate_trajectory, trajectory_size

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")

MAX_CODE_LENGTH = 20_000


class SubmissionRequest(BaseModel):
    """练习提交体，按题型选择对应字段。"""

    answer_index: int | None = None
    answer: str | None = None
    code: str | None = None
    trajectory: dict | None = None


@router.post("/exercises/{exercise_id}/submit")
def submit_exercise(
    exercise_id: str,
    payload: SubmissionRequest,
    user: User = Depends(require_api_user),
    _csrf: None = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    """判定练习并写入练习进度；编程题内部错误不写入进度。"""
    exercise = get_catalog().get_exercise(exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="练习不存在")
    if exercise.type == "local_task":
        raise HTTPException(status_code=400, detail="本地作业请使用标记完成")
    if exercise.type == "coding" and JUDGE_MODE == "disabled":
        raise HTTPException(status_code=403, detail="线上暂不开放编程判题")
    if not rate_limiter.allow(f"submit:{user.id}", *SUBMIT_LIMIT):
        raise HTTPException(status_code=429, detail="提交过于频繁，请稍后再试")

    if exercise.type == "trajectory_task":
        return _submit_trajectory(db, user.id, exercise, payload)

    try:
        result = _judge(exercise, payload)
    except HTTPException:
        raise
    except Exception:
        logger.exception("判题服务异常：exercise=%s", exercise_id)
        return JSONResponse(
            status_code=500,
            content={
                "status": "internal_error",
                "message": "判题服务异常，请稍后重试",
                "lesson_completed": False,
                "test_results": [],
            },
        )

    last_answer = _submission_text(exercise, payload)
    _save_exercise_progress(
        db, user.id, exercise.id, result.status, last_answer
    )
    lesson_completed = _sync_lesson_completion(
        db, user.id, exercise.lesson_id
    )

    return {
        "status": result.status,
        "message": result.message,
        "lesson_completed": lesson_completed,
        "test_results": result.test_results,
    }


def _submit_trajectory(
    db: Session,
    user_id: int,
    exercise: Exercise,
    payload: SubmissionRequest,
):
    """轨迹题只解析 JSON 并跑规则，不执行代码、不调用 LLM。"""
    if payload.trajectory is None:
        raise HTTPException(status_code=400, detail="轨迹题需要提交 trajectory")
    if trajectory_size(payload.trajectory) > MAX_JSON_BYTES:
        raise HTTPException(status_code=400, detail="轨迹 JSON 不能超过 100KB")

    try:
        result = evaluate_trajectory(exercise, payload.trajectory)
    except Exception:
        logger.exception("轨迹判定异常：exercise=%s", exercise.id)
        return JSONResponse(
            status_code=500,
            content={
                "status": "internal_error",
                "message": "轨迹判定异常，请稍后重试",
                "lesson_completed": False,
                "rule_results": [],
                "step_count": 0,
            },
        )

    last_answer = json.dumps(payload.trajectory, ensure_ascii=False)
    _save_exercise_progress(
        db, user_id, exercise.id, result["status"], last_answer
    )
    lesson_completed = _sync_lesson_completion(db, user_id, exercise.lesson_id)

    return {
        "status": result["status"],
        "message": result["message"],
        "lesson_completed": lesson_completed,
        "rule_results": result["rule_results"],
        "step_count": result["step_count"],
    }


@router.post("/exercises/{exercise_id}/complete")
def complete_local_task(
    exercise_id: str,
    user: User = Depends(require_api_user),
    _csrf: None = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    """本地作业标记完成；不执行代码、不保存提交内容，重复调用幂等。"""
    exercise = get_catalog().get_exercise(exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="练习不存在")
    if exercise.type != "local_task":
        raise HTTPException(status_code=400, detail="该练习不是本地作业")
    if not rate_limiter.allow(f"complete-ex:{user.id}", *COMPLETE_LIMIT):
        raise HTTPException(status_code=429, detail="操作过于频繁，请稍后再试")

    existing = db.scalar(
        select(ExerciseProgress).where(
            ExerciseProgress.user_id == user.id,
            ExerciseProgress.exercise_id == exercise.id,
        )
    )
    if existing is not None and existing.status == "accepted":
        return {
            "status": "accepted",
            "message": "本地作业已完成",
            "lesson_completed": _sync_lesson_completion(
                db, user.id, exercise.lesson_id
            ),
        }

    _save_exercise_progress(db, user.id, exercise.id, "accepted", None)
    lesson_completed = _sync_lesson_completion(db, user.id, exercise.lesson_id)
    return {
        "status": "accepted",
        "message": "本地作业已完成",
        "lesson_completed": lesson_completed,
    }


@router.post("/lessons/{lesson_id}/complete")
def complete_lesson(
    lesson_id: str,
    user: User = Depends(require_api_user),
    _csrf: None = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    """无练习课时的手动完成；重复调用保持幂等。"""
    lesson = get_catalog().get_lesson(lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="课时不存在")
    if lesson.exercise_ids:
        raise HTTPException(
            status_code=400,
            detail="本课有练习，需全部通过后自动完成",
        )
    if not rate_limiter.allow(f"complete-lesson:{user.id}", *COMPLETE_LIMIT):
        raise HTTPException(status_code=429, detail="操作过于频繁，请稍后再试")

    existing = db.scalar(
        select(LessonProgress).where(
            LessonProgress.user_id == user.id,
            LessonProgress.lesson_id == lesson_id,
        )
    )
    if existing is not None and existing.status == "completed":
        return {
            "status": "completed",
            "message": "本课已完成",
            "lesson_completed": True,
        }

    if existing is None:
        db.add(
            LessonProgress(
                user_id=user.id,
                lesson_id=lesson_id,
                status="completed",
                updated_at=utc_now_iso(),
            )
        )
    else:
        existing.status = "completed"
        existing.updated_at = utc_now_iso()
    db.commit()

    return {
        "status": "completed",
        "message": "本课已完成",
        "lesson_completed": True,
    }


def _judge(exercise: Exercise, payload: SubmissionRequest) -> JudgeResult:
    """按题型分发判定逻辑，并做必要的输入校验。"""
    if exercise.type == "single_choice":
        if payload.answer_index is None or not 0 <= payload.answer_index < len(
            exercise.options
        ):
            raise HTTPException(status_code=400, detail="请选择一个有效选项")
        return judge_choice(exercise, payload.answer_index)

    if exercise.type == "fill_blank":
        if payload.answer is None or not payload.answer.strip():
            raise HTTPException(status_code=400, detail="请填写答案")
        return judge_fill(exercise, payload.answer)

    if payload.code is None or not payload.code.strip():
        raise HTTPException(status_code=400, detail="请先编写代码")
    if len(payload.code) > MAX_CODE_LENGTH:
        raise HTTPException(status_code=400, detail="代码过长，请精简后提交")
    return judge_coding(exercise, payload.code)


def _submission_text(exercise: Exercise, payload: SubmissionRequest) -> str:
    """把三类提交统一转成可保存的最新作答内容。"""
    if exercise.type == "single_choice":
        return str(payload.answer_index)
    if exercise.type == "fill_blank":
        return payload.answer or ""
    return payload.code or ""


def _save_exercise_progress(
    db: Session,
    user_id: int,
    exercise_id: str,
    status: str,
    last_answer: str | None,
) -> None:
    """写入或更新练习最新状态、提交次数与最新作答内容。"""
    progress = db.scalar(
        select(ExerciseProgress).where(
            ExerciseProgress.user_id == user_id,
            ExerciseProgress.exercise_id == exercise_id,
        )
    )
    if progress is None:
        progress = ExerciseProgress(
            user_id=user_id,
            exercise_id=exercise_id,
            status=status,
            attempts=0,
            updated_at=utc_now_iso(),
        )
        db.add(progress)

    progress.status = status
    progress.attempts += 1
    progress.last_answer = last_answer
    progress.updated_at = utc_now_iso()
    db.commit()


def _sync_lesson_completion(db: Session, user_id: int, lesson_id: str) -> bool:
    """当本课全部练习通过时写入 lesson_progress；已完成的课时不回退。"""
    lesson = get_catalog().get_lesson(lesson_id)
    if lesson is None or not lesson.exercise_ids:
        return False

    existing = db.scalar(
        select(LessonProgress).where(
            LessonProgress.user_id == user_id,
            LessonProgress.lesson_id == lesson_id,
        )
    )
    if existing is not None and existing.status == "completed":
        return True

    accepted_ids = set(
        db.scalars(
            select(ExerciseProgress.exercise_id).where(
                ExerciseProgress.user_id == user_id,
                ExerciseProgress.status == "accepted",
                ExerciseProgress.exercise_id.in_(lesson.exercise_ids),
            )
        ).all()
    )
    if not set(lesson.exercise_ids) <= accepted_ids:
        return False

    if existing is None:
        db.add(
            LessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                status="completed",
                updated_at=utc_now_iso(),
            )
        )
    else:
        existing.status = "completed"
        existing.updated_at = utc_now_iso()
    db.commit()
    return True
