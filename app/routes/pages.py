"""课程目录、学习路线与课时页面。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_user
from app.config import JUDGE_MODE, TEMPLATES_DIR
from app.content import get_catalog
from app.db import get_db
from app.models import ExerciseProgress, LessonProgress, User
from app.security import get_csrf_token

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/")
def index(request: Request):
    """首页只做分流：已登录去课程目录，未登录去登录页。"""
    if request.session.get("user_id"):
        return RedirectResponse("/courses", status_code=303)
    return RedirectResponse("/login", status_code=303)


@router.get("/roadmap", response_class=HTMLResponse)
def legacy_roadmap():
    """兼容旧入口：默认进入 Python 课程路线。"""
    return RedirectResponse("/courses/python/roadmap", status_code=303)


@router.get("/courses", response_class=HTMLResponse)
def course_catalog(
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """展示全部课程、完成度与先修关系。"""
    catalog = get_catalog()
    completed = _completed_lesson_ids(db, user.id)
    course_items = []

    for course in catalog.ordered_courses:
        progress = _course_progress(course, completed)
        prerequisite_course = (
            catalog.get_course(course.prerequisite) if course.prerequisite else None
        )
        course_items.append(
            {
                "course": course,
                "progress": progress,
                "prerequisite_course": prerequisite_course,
                "prerequisite_completed": _course_completed(
                    prerequisite_course, completed
                ),
            }
        )

    return templates.TemplateResponse(
        "courses.html",
        {
            "request": request,
            "user": user,
            "course_items": course_items,
            "csrf_token": get_csrf_token(request),
        },
    )


@router.get("/courses/{course_id}/roadmap", response_class=HTMLResponse)
def roadmap(
    request: Request,
    course_id: str,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """按课程展示章节、课时与完成度。"""
    catalog = get_catalog()
    course = catalog.get_course(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="课程不存在")

    completed = _completed_lesson_ids(db, user.id)
    prerequisite_course = (
        catalog.get_course(course.prerequisite) if course.prerequisite else None
    )

    return templates.TemplateResponse(
        "roadmap.html",
        {
            "request": request,
            "user": user,
            "course": course,
            "completed_lesson_ids": completed,
            "progress_percent": _course_progress(course, completed),
            "continue_lesson": course.continue_lesson(completed),
            "prerequisite_course": prerequisite_course,
            "prerequisite_completed": _course_completed(
                prerequisite_course, completed
            ),
            "csrf_token": get_csrf_token(request),
            "judge_mode": JUDGE_MODE,
        },
    )


@router.get("/courses/{course_id}/lessons/{lesson_id}", response_class=HTMLResponse)
def lesson_page(
    request: Request,
    course_id: str,
    lesson_id: str,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """渲染课时正文、练习与上下课导航。"""
    catalog = get_catalog()
    course = catalog.get_course(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="课程不存在")

    lesson = catalog.get_lesson(lesson_id)
    if lesson is None or lesson.course_id != course_id:
        raise HTTPException(status_code=404, detail="课时不存在")

    completed = _completed_lesson_ids(db, user.id)
    exercise_states = _exercise_states(db, user.id, lesson)
    prev_lesson = (
        course.get_lesson(lesson.prev_lesson_id) if lesson.prev_lesson_id else None
    )
    next_lesson = (
        course.get_lesson(lesson.next_lesson_id) if lesson.next_lesson_id else None
    )

    return templates.TemplateResponse(
        "lesson.html",
        {
            "request": request,
            "user": user,
            "course": course,
            "stage": course.get_stage_for_lesson(lesson),
            "lesson": lesson,
            "completed_lesson_ids": completed,
            "exercise_states": exercise_states,
            "prev_lesson": prev_lesson,
            "next_lesson": next_lesson,
            "csrf_token": get_csrf_token(request),
            "judge_mode": JUDGE_MODE,
        },
    )


@router.get("/lessons/{lesson_id}", response_class=HTMLResponse)
def legacy_lesson_page(
    lesson_id: str,
    user: User = Depends(require_user),
):
    """兼容旧链接：按课时 ID 跳转到所属课程。"""
    lesson = get_catalog().get_lesson(lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="课时不存在")
    return RedirectResponse(
        f"/courses/{lesson.course_id}/lessons/{lesson_id}",
        status_code=303,
    )


def _course_progress(course, completed_ids: set[str]) -> int:
    """按本课程课时计算完成度，四舍五入取整。"""
    if not course.lessons:
        return 0
    done = sum(1 for lesson in course.lessons if lesson.id in completed_ids)
    return int(done / course.total_lessons * 100 + 0.5)


def _course_completed(course, completed_ids: set[str]) -> bool:
    """判断先修课程是否全部完成。"""
    if course is None:
        return False
    return {lesson.id for lesson in course.lessons} <= completed_ids


def _completed_lesson_ids(db: Session, user_id: int) -> set[str]:
    """查询当前用户已完成课时 ID。"""
    lesson_ids = db.scalars(
        select(LessonProgress.lesson_id).where(
            LessonProgress.user_id == user_id,
            LessonProgress.status == "completed",
        )
    ).all()
    return set(lesson_ids)


def _exercise_states(
    db: Session, user_id: int, lesson
) -> dict[str, dict]:
    """读取本课练习的最新状态与最新作答，供页面回填。"""
    if not lesson.exercises:
        return {}

    exercise_ids = [exercise.id for exercise in lesson.exercises]
    rows = db.scalars(
        select(ExerciseProgress).where(
            ExerciseProgress.user_id == user_id,
            ExerciseProgress.exercise_id.in_(exercise_ids),
        )
    ).all()
    by_id = {row.exercise_id: row for row in rows}

    states: dict[str, dict] = {}
    for exercise in lesson.exercises:
        row = by_id.get(exercise.id)
        last_answer = row.last_answer if row and row.last_answer else ""
        last_index = None
        if exercise.type == "single_choice" and last_answer.isdigit():
            last_index = int(last_answer)
        states[exercise.id] = {
            "status": row.status if row else None,
            "attempts": row.attempts if row else 0,
            "last_answer": last_answer,
            "last_index": last_index,
        }
    return states
