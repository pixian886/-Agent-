"""本地启动脚本：建库、写入演示账号并启动 Uvicorn。"""

from __future__ import annotations

import os

import uvicorn

from app.config import APP_ENV, HOST, PORT, ensure_data_dir, load_or_create_secret_key


def main() -> None:
    ensure_data_dir()
    # 生产环境必须显式提供固定密钥，不能自动生成。
    if APP_ENV == "production" and not os.getenv("APP_SECRET_KEY"):
        raise RuntimeError("APP_ENV=production 时必须设置 APP_SECRET_KEY")

    # 会话密钥必须在导入应用前准备好，保证重启后登录态仍然有效。
    os.environ.setdefault("APP_SECRET_KEY", load_or_create_secret_key())

    from app.db import init_db
    from app.seed import ensure_demo_user

    init_db()
    ensure_demo_user()

    print(f"从零开始Agent学习已启动：http://{HOST}:{PORT}")
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False)


if __name__ == "__main__":
    main()
