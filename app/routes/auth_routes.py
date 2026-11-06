"""注册、登录与退出路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import (
    hash_password,
    is_logged_in,
    is_valid_password,
    is_valid_username,
    login_user,
    logout_user,
    verify_password,
)
from app.config import TEMPLATES_DIR
from app.db import get_db
from app.models import User
from app.security import (
    LOGIN_LIMIT,
    REGISTER_LIMIT,
    client_ip,
    get_csrf_token,
    rate_limiter,
    validate_csrf,
)

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """已登录用户直接进入路线页。"""
    if is_logged_in(request):
        return RedirectResponse("/roadmap", status_code=303)

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "user": None,
            "error": None,
            "username": "",
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    """校验 CSRF、限流与账号密码，成功后写入 Session。"""
    validate_csrf(request, csrf_token)
    username = username.strip()

    login_key = f"login:{client_ip(request)}:{username}"
    if not rate_limiter.allow(login_key, *LOGIN_LIMIT):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "user": None,
                "error": "尝试次数过多，请 15 分钟后再试",
                "username": username,
                "csrf_token": get_csrf_token(request),
            },
            status_code=429,
        )

    user = db.scalar(select(User).where(User.username == username))

    # 不区分“用户不存在”和“密码错误”，避免泄露账号是否存在。
    if user is None or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "user": None,
                "error": "用户名或密码错误",
                "username": username,
                "csrf_token": get_csrf_token(request),
            },
            status_code=400,
        )

    rate_limiter.reset(login_key)
    login_user(request, user)
    return RedirectResponse("/roadmap", status_code=303)


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    """已登录用户不需要注册。"""
    if is_logged_in(request):
        return RedirectResponse("/roadmap", status_code=303)

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "user": None,
            "error": None,
            "username": "",
            "csrf_token": get_csrf_token(request),
        },
    )


@router.post("/register", response_class=HTMLResponse)
def register_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    """校验 CSRF、限流与表单，写入用户并自动登录。"""
    validate_csrf(request, csrf_token)
    username = username.strip()

    register_key = f"register:{client_ip(request)}"
    if not rate_limiter.allow(register_key, *REGISTER_LIMIT):
        return _render_register_error(
            request, username, "注册过于频繁，请稍后再试", status_code=429
        )

    error = _validate_registration(username, password, confirm_password)
    if error is not None:
        return _render_register_error(request, username, error)

    existing = db.scalar(select(User.id).where(User.username == username))
    if existing is not None:
        return _render_register_error(request, username, "该用户名已被使用")

    user = User(username=username, password_hash=hash_password(password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # 并发注册同名用户时，唯一索引会在这里兜底。
        db.rollback()
        return _render_register_error(request, username, "该用户名已被使用")

    db.refresh(user)
    login_user(request, user)
    return RedirectResponse("/roadmap", status_code=303)


@router.post("/logout")
def logout(request: Request, csrf_token: str = Form("")):
    """校验 CSRF 后退出登录并回到登录页。"""
    validate_csrf(request, csrf_token)
    logout_user(request)
    return RedirectResponse("/login", status_code=303)


def _validate_registration(
    username: str, password: str, confirm_password: str
) -> str | None:
    """返回第一条表单错误；全部通过时返回 None。"""
    if not is_valid_username(username):
        return "用户名需为 3~20 个字符，可使用中文、字母、数字和下划线"
    if not is_valid_password(password):
        return "密码长度需为 6~64 位"
    if password != confirm_password:
        return "两次输入的密码不一致"
    return None


def _render_register_error(
    request: Request,
    username: str,
    error: str,
    status_code: int = 400,
):
    """注册失败时保留用户名并返回错误。"""
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "user": None,
            "error": error,
            "username": username,
            "csrf_token": get_csrf_token(request),
        },
        status_code=status_code,
    )
