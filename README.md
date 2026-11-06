# 从零开始Agent学习

面向编程初学者的 Agent 学习平台：先完成 Python 先修，再进入 Agent 开发全流程。课程主线为：

**Python 先修 → 真实 API → 工具调用 → ReAct → 记忆与 RAG → MCP 与安全 → 评测与成本 → 多 Agent → 结业项目**

当前进度：**M7 交付验收、M8 Agent 先修、M9 上线加固、M10 部署产物、M11 多课程底座、M12 轨迹题引擎、M13 A0–A3 内容、M14 A4–A7 内容、M15 结业项目与验收已完成**。Agent 课程 24 课全部上线，合计 37 道练习。

## 环境要求

- Python 3.10 及以上（当前开发环境为 Python 3.13）
- Windows 10/11（也兼容 macOS / Linux）
- 不需要 Node、Docker、PostgreSQL

## 启动方式

### 方式一：Windows 一键启动

双击 `start.bat`。脚本会自动创建虚拟环境、安装依赖并启动服务。

### 方式二：手动启动

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

浏览器访问：

```text
http://127.0.0.1:8000
```

健康检查：

```text
http://127.0.0.1:8000/health
```

## 演示账号

首次启动会自动写入：

```text
用户名：demo
密码：demo123
```

打开首页会跳转到登录页，可直接使用演示账号登录。

## 环境变量（M9）

复制 `.env.example` 后按需修改；本地直接 `python run.py` 时不读取 `.env`，可在启动前设置环境变量。

| 变量 | 默认 | 说明 |
|-|-|-|
| `APP_ENV` | `local` | `production` 时强制要求 `APP_SECRET_KEY` |
| `APP_SECRET_KEY` | 自动生成 | 线上必须固定注入 |
| `DATABASE_URL` | `sqlite:///data/app.db` | 可覆盖数据库连接串 |
| `HTTPS_ONLY` | `production` 为 `true` | 启用 Secure Cookie 与 HSTS |
| `TRUST_PROXY` | `false` | 在 Caddy/Nginx 后设为 `true` |
| `JUDGE_MODE` | `subprocess` | `subprocess` / `docker` / `disabled` |
| `JUDGE_DOCKER_IMAGE` | `plg-judge:latest` | 判题容器镜像 |
| `JUDGE_CONCURRENCY` | `2` | 判题容器并发，范围 1~4 |
| `PORT` | `8000` | 本地监听端口 |

## 当前功能

- 项目目录与 FastAPI 应用骨架
- SQLite 数据文件 `data/app.db`
- 三张表：`users`、`lesson_progress`、`exercise_progress`
- 演示账号自动初始化
- 注册、登录、退出
- Session 签名 Cookie，登录保持 7 天
- 用户名与密码服务端校验
- 未登录访问受保护页面时跳转登录页
- 6 章 11 课学习路线与完成度
- 11 节课均配有概念卡、对比卡、提示卡或步骤动画
- 概念卡、对比卡、提示卡支持点击放大；支持 Esc、遮罩与关闭按钮
- 课时页：Markdown 正文、图文卡片、步骤动画、上下课导航
- 21 道练习：2 道单选、1 道填空、15 道站内编程题、3 道本地作业
- 新增 L07 JSON 与文件读写、L08 HTTP 与真实 API、L09 异常与环境变量
- 本地作业提供任务说明、起步代码、常见报错与折叠参考答案，点击「标记完成」记录进度
- HTTP 类站内题由判题器内置 mock 服务判题，不依赖外网
- 刷新课时页后恢复上次选择、填空答案或代码
- 通过后锁定作答并可点击「重做」；错误可继续修改；界面不显示提交次数
- 编程题可展开查看测试用例（输入与期望输出）
- 编程题在临时目录执行，支持通过、答案错误、超时、运行错误
- 练习最新状态与作答内容写入 `exercise_progress`（提交次数仅内部统计）
- 本课全部练习（含本地作业）完成后自动完成课时
- L11 项目任务可手动「标记完成」
- 学习路线实时显示完成度与继续学习入口
- 会话密钥持久化到 `data/secret_key`
- `/health` 健康检查
- 所有 POST 校验 CSRF：表单带隐藏字段，JSON 请求带 `X-CSRF-Token`
- 登录按 IP + 用户名限流，注册按 IP 限流，提交与完成按用户限流
- 安全响应头：CSP、X-Frame-Options、X-Content-Type-Options、Referrer-Policy
- SQLite 启用 WAL、`synchronous=NORMAL` 与 `busy_timeout=5000`
- `APP_ENV`、`HTTPS_ONLY`、`TRUST_PROXY`、`JUDGE_MODE` 环境变量配置
- `JUDGE_MODE=disabled` 可关闭编程判题，只保留选择、填空与本地作业
- `JUDGE_MODE=docker` 使用一次性容器判题：无网络、内存/CPU/PID 限制、只读根目录、非 root
- `deploy/` 提供应用镜像、判题镜像、Compose 与 Caddy 配置
- `DEPLOY.md` 提供云服务器部署、备份、升级与排查步骤
- 课程目录 `/courses`：Python 与 Agent 双课程，进度独立
- Agent 课程路线：第 0 章 + 7 章 + 结业项目，共 24 课
- a00「AI 时代名词地图」已上线：名词关系图、对比卡与两道练习
- 第 1–3 章正文已上线：真实 API、提示词工程、消息参数、错误重试、工具调用、工具注册表、ReAct 循环与失败轨迹
- 第 4–7 章正文已上线：对话记忆、分块检索、RAG、上下文工程、MCP、工具安全、评测、成本限流、多 Agent 与框架对照
- 结业项目 a22–a23 已上线：项目设计单、从空目录到可运行 Agent 的六文件跟做教程、交付清单、3 分钟演示脚本与多工具结业轨迹
- Agent 课程合计 37 道练习：单选、填空、站内编程、本地作业与轨迹题
- 编程题提供折叠参考答案：先自己尝试，实在不会再点开；24 道参考解全部通过测试用例
- 轨迹题 `trajectory_task`：粘贴轨迹 JSON，按 8 类规则逐条判定，显示时间线与规则结果
- 轨迹题只解析 JSON，不执行代码、不访问网络、不调用模型；100KB / 50 步 / 单字符串 2000 字符上限

## 验收材料

- [验收记录](docs/验收记录.md)：启动、账号、路线、课时、判题、进度与截图索引；
- [验收截图](docs/screenshots/)：登录、路线、课时、测试用例、判题结果、项目完成与 100% 路线；
- [启动记录](docs/screenshots/10-startup.txt)：实际启动输出与 `/health` 结果。

## 项目完成状态

v1.0 实践周功能、M8 Agent 先修、M9 上线加固、M10 部署产物、M11 多课程底座、M12 轨迹题引擎、M13 A0–A3 内容、M14 A4–A7 内容与 M15 结业项目及验收已完成。容器运行与 HTTPS 证书需要在部署服务器上按 `DEPLOY.md` 验证。后续：

- 在装有 Docker 的服务器上验证容器判题与 HTTPS；
- 提交历史与错题本；
- 教师后台与内容编辑；
- 更严格的判题沙箱与隐藏测试用例。

## 项目结构

```text
Programming Learning Guide/
├── app/
│   ├── main.py             # FastAPI 入口
│   ├── config.py           # 路径与运行配置
│   ├── db.py               # 数据库引擎与会话
│   ├── models.py           # 用户、课时进度、练习进度
│   ├── auth.py             # 密码哈希、登录态与表单校验
│   ├── content.py          # 课程加载、校验与 Markdown 渲染
│   ├── judge.py            # 站内判题与 mock HTTP 夹具
│   ├── trajectory.py       # 轨迹题 JSON 校验与规则判定
│   ├── seed.py             # 演示账号初始化
│   ├── routes/
│   │   ├── auth_routes.py  # 注册、登录、退出
│   │   ├── api.py          # 练习提交、本地作业完成与进度写入
│   │   └── pages.py        # 首页分流、课程目录、路线页、课时页
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── courses.html
│   │   ├── roadmap.html
│   │   ├── lesson.html
│   │   └── _exercise_preview.html
│   └── static/
│       ├── style.css
│       ├── app.js
│       └── img/            # 本地 SVG 图示（含 JSON、文件、HTTP、异常、Key）
├── content/
│   ├── course.json         # Python 课程
│   ├── exercises.json      # Python 练习
│   ├── lessons/            # Python 课时
│   ├── agent_course.json   # Agent 课程
│   ├── agent_exercises.json
│   └── agent_lessons/
│       ├── a00.md–a21.md   # 第 0–7 章正文
│       └── a22.md–a23.md   # 结业项目
├── docs/
│   ├── 验收记录.md
│   └── screenshots/        # 验收截图与启动记录
├── data/                   # 运行时生成，不提交
├── PRD.md
├── 系统设计.md
├── 开发说明.md
├── AGENT_PRD.md            # Agent 课程需求文档
├── AGENT_系统设计.md       # Agent 课程系统设计
├── run.py                  # 启动脚本
├── start.bat               # Windows 一键启动
├── .env.example            # 本地环境变量模板
├── DEPLOY.md               # M10 云服务器部署说明
├── deploy/
│   ├── Dockerfile          # 应用镜像（含 Docker CLI）
│   ├── judge.Dockerfile    # 判题镜像（Python + requests）
│   ├── docker-compose.yml  # app + Caddy + 判题镜像
│   ├── Caddyfile           # HTTPS 与反向代理
│   └── .env.example        # 线上环境变量模板
└── requirements.txt
```

## 重置数据

停止服务后删除 `data/app.db`，重新启动会自动建表并写入演示账号。

## 提交或拷贝给教师时

不要包含以下目录或文件：

- `.venv/`：虚拟环境与操作系统绑定，拷到另一台电脑可能无法使用；
- `data/`：包含本地数据库与会话密钥，首次启动会自动生成；
- `__pycache__/`、`.screenshots/`：缓存文件。

教师拿到项目后，双击 `start.bat` 会自动创建虚拟环境、安装依赖并初始化数据。

## 安全边界

本项目的站内判题会在本机执行提交的 Python 代码，**不是安全沙箱**。M9 已加入 CSRF、限流与安全响应头；M10 提供 Docker 判题产物，但挂载 Docker socket 等于把宿主机 Docker 控制权交给应用容器，**只在可信服务器使用**。无法接受时设置 `JUDGE_MODE=disabled`，关闭站内编程判题。

## 常见问题

**1. 提示找不到 python 命令**

安装 Python 时勾选 `Add python.exe to PATH`，或使用 `py` 命令代替 `python`。

**2. 8000 端口被占用**

使用环境变量换端口：

```bat
set PORT=8001
python run.py
```

**3. 依赖安装失败**

确认网络可用，或在有网络的电脑上执行 `pip download -r requirements.txt -d wheels`，把 `wheels` 目录一起拷贝到离线电脑后安装。

**4. 页面没有样式，或与之前看到的画面不同**

先确认浏览器访问的是 `http://127.0.0.1:8000`，不要直接双击 HTML 文件；然后按 `Ctrl+F5` 强制刷新。静态资源已经带版本参数 `?v=13`，强制刷新后会加载最新样式。如果仍然无效，在开发者工具的 Network 中检查 `style.css?v=13` 是否返回 200，并确认没有旧服务占用 8000 端口。

## 下一步

M15 已完成，M1–M15 全部里程碑收尾。下一步是在装有 Docker 的服务器上按 `DEPLOY.md` 验证容器判题与 HTTPS；之后按教学反馈补充内容与可选功能。
