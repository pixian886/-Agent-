# 《从零开始Agent学习》项目需求文档（PRD）

> 版本：v2.2  
> 日期：2026-11-03  
> 项目类型：实践周课程项目  
> 文档用途：既作为需求文档，也作为 AI 编码与验收的执行依据  
> 当前状态：v1.0 交付验收、M8 Agent 先修、M9 上线加固已完成；M10 部署产物已完成，容器运行待部署服务器验证

---

## 0. 文档说明

- 本项目是**实践周课程作业**，目标是交付一个**功能闭环、可本地运行、可演示**的 Web 应用，不追求生产级完整度。
- 验收的硬标准只有两条：
  1. 核心功能能够实际操作并得到正确结果；
  2. 验收者拿到项目后，按 README 能在一台普通电脑上成功运行。
- v2.0 在 v1.0 已交付的基础上扩展，不改动已有功能：新增 3 节 Agent 先修课、10 道练习、`local_task` 题型，并补充上线部署的安全与运行要求。
- v2.0 的目标是：学员完成本课程后，具备进入 Agent 开发所需的 Python、JSON、HTTP、异常与密钥管理基础。
- 本文档第 5 章为技术定稿，AI 可直接按此实施，不需要再做架构决策。

---

## 1. 项目概述

### 1.1 背景与痛点

编程初学者面对的最大问题不是“资料不够”，而是：

- 不知道先学什么、后学什么，学习顺序混乱；
- 教程、视频、文档分散，缺少一条连贯的主线；
- 看懂了但写不出，缺少即时练习和反馈；
- 学完语法不知道怎么用，缺少一个可完成的小项目。

### 1.2 项目定位

**面向编程小白的 Python 学习平台，同时作为 Agent 开发的前置课程。**

用一条清晰的学习路线，把「环境配置 → 基础语法 → 核心语法 → 连接外部世界 → 数据库 → Web 应用实战」串起来，为后续 Agent 开发打基础。抽象概念用图文卡片和分步动画讲解，避免大段纯文字；每节课配套练习，简单编程题可在站内判题，复杂案例题在学员本机完成并提供参考答案。

### 1.3 项目目标

| 目标 | 说明 |
|-|-|
| 路径清晰 | 用户打开首页就知道当前该学哪一课 |
| 学练结合 | 每节课至少一个练习；简单题站内判题，复杂案例题本地完成并提供答案 |
| Agent 先修 | 覆盖 JSON、HTTP、异常、环境变量与依赖管理，能平滑进入 Agent 开发 |
| 内容生动 | 抽象概念用图文卡片和分步动画讲解，避免大段纯文字 |
| 进度可见 | 完成情况被记录，刷新和重启后不丢失 |
| 易于验收 | 一条命令启动，在任意一台电脑上即可完整走通流程 |

### 1.4 目标用户

| 角色 | 描述 | 核心诉求 |
|-|-|-|
| 学习者 | 零基础或刚入门的编程初学者 | 知道学什么、能练习、能看到进步 |
| 内容维护者 | 开发者本人 | 直接改文件即可维护课程，不需要后台 |

### 1.5 项目范围

- Web 应用，默认本地运行，v2 支持部署到公网；
- Python 单一语言教学，定位为 Agent 开发前置；
- 课程路线、课时正文、图文卡片、分步动画、概念题、站内编程题、本地作业；
- 用户名密码登录、学习进度保存；
- 课程内容：6 章 11 课，含正文、21 道练习与 1 个项目任务；
- v2 新增：JSON、HTTP、异常与环境变量三课，`local_task` 题型，mock HTTP 判题，上线安全加固。

### 1.6 成功标准

1. 验收者按 README 完成安装并启动，浏览器能打开首页；
2. 新用户可注册、登录、退出；
3. 学习路线页正确显示 6 个章节、11 节课与完成状态；
4. 课时页 Markdown 正常渲染，代码块显示正常；
5. 视觉卡片正常展示，步骤动画可上一步、下一步、重播；
6. 单选题、填空题提交后立即返回对错；
7. 站内编程题提交后返回判题结果，正确/错误/超时/运行错误四类结果均可复现；
8. 本地作业可查看任务、参考答案，并「标记完成」；
9. 完成一节课的全部练习（含本地作业）后，课时状态变为已完成，路线完成度同步更新；
10. 重启服务后，账号与进度仍然存在；
11. 本地运行不依赖外网 CDN、Node、Docker；线上部署按 5.9 启用 HTTPS、CSRF 与判题沙箱。

---

## 2. 用户角色与核心流程

### 2.1 角色定义

| 角色 | 权限 |
|-|-|
| 未登录访客 | 只能访问登录页、注册页 |
| 学习者 | 访问路线、课时、提交练习、查看自己的进度 |

### 2.2 核心学习流程（文字描述）

1. 用户首次访问，进入登录页，选择注册；
2. 注册成功自动登录，进入学习路线页；
3. 路线页展示 6 个章节，每章下列出课时及完成状态；
4. 用户点击「继续学习」，进入第一个未完成课时；
5. 阅读课时正文（Markdown 渲染 + 图文卡片 + 分步动画），完成页面内的练习；
6. 概念题提交后即时判定；站内编程题提交后由后端执行并返回结果；
7. 本地作业在学员本机完成，页面提供任务说明、起步代码与参考答案，学员确认后点「标记完成」；
8. 有练习的课时，全部练习（含本地作业）为 `accepted` 后自动完成；无练习的课时，点击「标记完成」结束；
9. 用户通过上一课/下一课导航继续学习；
10. 返回路线页，完成度百分比更新。

### 2.3 页面流转

```
登录/注册
   ↓
学习路线页 /roadmap
   ↓
课时页 /lessons/{lesson_id}
   ↓
练习提交（概念题即时判定 / 编程题后端判题）
   ↓
结果反馈 + 进度更新
   ↓
返回路线页或进入下一课
```

---

## 3. 功能需求

### 3.1 功能列表

| 编号 | 功能 | 描述 | 验收标准 |
|-|-|-|-|
| F-01 | 用户注册 | 用户名 + 密码注册 | 用户名 3~20 字符、密码不少于 6 位；重复用户名有明确提示；注册成功自动登录 |
| F-02 | 用户登录/退出 | 会话保持与退出 | 正确凭证可登录；错误凭证提示失败；刷新页面保持登录；退出后访问受保护页面跳转登录页 |
| F-03 | 学习路线页 | 展示章节、课时、完成状态、总完成度 | 6 个章节、11 节课按顺序展示；每课显示未开始/已完成；顶部显示完成百分比；提供「继续学习」入口 |
| F-04 | 课时内容阅读 | 渲染 Markdown 正文与视觉组件 | 标题、段落、列表、代码块、表格、链接正常显示；视觉卡片与步骤动画正常渲染；代码块等宽字体且可横向滚动；提供上一课/下一课导航 |
| F-05 | 单选题 | 选择答案并提交 | 提交后立即返回正确/错误；答错显示正确答案与解析；错误可继续重做；通过后锁定作答并显示「重做」；刷新页面后恢复上次选择 |
| F-06 | 填空题 | 输入答案并提交 | 提交后立即返回正确/错误；比较时忽略首尾空白，默认忽略大小写；错误可继续重做；通过后锁定作答并显示「重做」；刷新页面后恢复上次输入 |
| F-07 | 编程题 | 编辑代码并提交判题 | 提供代码编辑区（等宽、支持 Tab 缩进）；提交后返回判题状态、耗时、失败用例的期望输出与实际输出；错误可继续修改重做；通过后锁定代码并显示「重做」；刷新页面后恢复上次代码 |
| F-08 | 判题结果 | 四类结果可区分 | 支持「通过 / 答案错误 / 超时 / 运行错误」；编程题可展开查看测试用例（输入/期望输出），提交后按用例展示结果；超时不超过 3 秒/用例；输出内容超长时截断显示 |
| F-09 | 学习进度 | 记录并展示进度 | 每课状态为未开始/已完成；有练习的课时，全部练习（含本地作业）为 `accepted` 后自动完成；无练习的课时可点击「标记完成」；完成度 = 已完成课时数 / 总课时数；重启服务后进度保留 |
| F-10 | 内容加载 | 从本地文件加载课程 | 启动时读取 `content/` 下配置与 Markdown；配置错误时启动失败并输出具体文件与原因；课程内容不存入数据库 |
| F-11 | 演示数据 | 首次启动即可体验 | 自动初始化数据库；内置演示账号 `demo / demo123`；课程骨架覆盖 6 个章节、11 节课；11 篇课时正文；2 道单选题、1 道填空题、15 道站内编程题、3 道本地作业、1 个项目任务；至少 6 篇正文包含视觉卡片，至少 3 篇包含步骤动画 |
| F-12 | 本地启动 | 可独立运行 | 提供 README 与 `start.bat`；首次启动自动建库；无需 Docker、Node、外部数据库；默认监听 `127.0.0.1:8000` |
| F-13 | 视觉卡片 | 用图文卡片呈现抽象概念 | 提供概念卡、对比卡、提示卡三种样式；卡片含图示/图片、标题与说明；布局在桌面端正常；图片缺失时显示 alt 文本；不引用外部图片；卡片可点击放大，支持 Esc、遮罩与关闭按钮 |
| F-14 | 步骤动画 | 用分步图解呈现执行过程 | 每个动画 2~4 步；支持上一步、下一步、重播；当前步骤高亮并显示 `当前 / 总数`；切换不刷新页面；无第三方动画库 |
| F-15 | 本地作业 | 复杂案例题在学员本机完成，平台提供任务说明、起步代码、参考答案与「标记完成」 | 任务卡包含说明、步骤、代码与折叠答案；点击「标记完成」写入完成状态；已完成可「重新练习」；不做代码检查、不执行代码、不上传文件 |
| F-16 | mock HTTP 判题 | HTTP 类站内题通过本地 mock 服务判题 | 判题器在隔离环境内启动固定响应的 mock 服务；学员代码请求 `127.0.0.1`；不依赖外网；超时仍为 3 秒 |
| F-17 | 在线部署支持 | 支持部署到公网 | 线上启用 HTTPS、Secure Cookie、CSRF、限流与安全响应头；判题按 `JUDGE_MODE` 选择 `docker` 或 `disabled`；配套 `Dockerfile`、`docker-compose.yml`、`DEPLOY.md` |

> F-01、F-02、F-04–F-08、F-10、F-12–F-14 随 v1.0 已完成；F-03、F-09、F-11 已按 v2 调整；F-15、F-16 已实现；F-17 的 HTTPS、CSRF、限流、安全头、WAL 与 Docker 判题代码已完成，Compose 容器运行待部署服务器验证。

### 3.2 关键业务规则

| 规则 | 定义 |
|-|-|
| 课时访问 | 不强制顺序解锁，所有课时可访问；「继续学习」仅做引导 |
| 课时完成 | 有练习的课时：该课全部练习（含本地作业）状态为 `accepted` 后自动完成；无练习的课时：显示「标记完成」按钮 |
| 进度不回退 | 课时一旦完成，后续重复练习不会取消完成状态 |
| 概念题判定 | 单选按选项索引比对；填空按去首尾空白、默认忽略大小写后比对 |
| 编程题判定 | 逐个测试用例执行，全部通过才算通过；遇到第一个失败用例即返回 |
| 输出比对 | 统一换行符为 `\n`，逐行去除行尾空白，忽略末尾空行 |
| 判题范围 | 站内编程题仅支持 Python 标准库，不支持 pip 安装第三方包；本地作业可使用第三方库、网络与真实 API |
| 题型边界 | 单文件、几十行以内、3 秒内、输出确定、无需网络的题放站内；多文件、需要第三方库、真实 API、数据库或 Web 服务的案例题放本地作业 |
| 本地作业完成 | 平台不检查代码、不执行代码、不上传文件；学员自行完成并点「标记完成」，状态写为 `accepted`；已完成可「重新练习」；界面不展示提交次数 |
| 答案展示 | 站内题只展示测试用例，不直接给答案；本地作业提供折叠的参考答案，学员自行决定何时查看 |
| 作答重试 | 提交错误后可继续修改重试；通过后锁定作答并显示「重做」；界面不展示提交次数 |
| 作答恢复 | 保存最新一次作答内容（选项索引 / 填空答案 / 代码），刷新课时页后回填；不保存提交历史 |
| 进度计算 | `已完成课时数 / 总课时数 × 100%`，四舍五入取整 |
| 视觉组件 | 以 HTML 片段嵌入 Markdown，样式与交互由全局 CSS/JS 提供，禁止在正文中写 `<script>` |
| 卡片放大 | 概念卡、对比卡、提示卡可点击放大；支持 Esc、遮罩与关闭按钮；放大层不改变正文内容 |
| 动画播放 | 默认停在第一步；切换不刷新页面；重播回到第一步；单个动画 2~4 步 |
| 素材来源 | 图片与图示全部存放在 `app/static/img/`，优先使用 SVG，禁止引用外链 |
| 项目任务课时 | L11 不配置自动判题练习，正文给出项目任务清单，课时使用「标记完成」按钮结束 |
| 课程顺序 | 新增三课插入“类与对象”之后；数据库与 Web 两课顺延为第 10、11 课 |

### 3.3 课程内容设计

课程名称：**Python 从零到 Web 应用 · Agent 先修**，共 6 章 11 课。

#### 3.3.1 课程总览

| 章节 | 课时 | 标题 | 练习 | 视觉 |
|-|-|-|-|-|
| 第一章 环境配置 | L01 | 安装 Python 并运行第一个程序 | 单选 + 编程 + 本地作业 | 概念卡 |
| 第二章 基础语法 | L02 | 变量与数据类型 | 填空 + 编程 | 概念卡 + 步骤动画 |
| 第二章 基础语法 | L03 | 条件与循环 | 单选 + 编程 × 2 | 对比卡 + 步骤动画 |
| 第三章 核心语法 | L04 | 函数 | 编程 × 2 | 概念卡 |
| 第三章 核心语法 | L05 | 列表与字典 | 编程 × 2 | 概念卡 |
| 第三章 核心语法 | L06 | 类与对象 | 编程 | 概念卡 |
| 第四章 连接外部世界 | L07 | JSON 与文件读写 | 编程 × 2 | 对比卡 + 步骤动画 |
| 第四章 连接外部世界 | L08 | HTTP 与真实 API | 编程 + 本地作业 | 概念卡 + 步骤动画 |
| 第四章 连接外部世界 | L09 | 异常、环境变量与密钥 | 编程 × 2 + 本地作业 | 概念卡 + 提示卡 |
| 第五章 数据库 | L10 | SQLite 与 CRUD | 编程 | 步骤动画 |
| 第六章 Web 实战 | L11 | 用 FastAPI 做留言板 | 项目任务 | 概念卡 |

#### 3.3.2 课时结构模板

每节课按以下顺序组织，正文控制在 600~1200 字，涉及新工具链的课可到 1500 字：

1. 学习目标：1~2 条，用「学完能做到」描述；
2. 概念讲解：至少 1 个视觉卡片；
3. 代码示例：可运行，并给出预期输出；
4. 步骤动画：重点课使用，2~4 步；
5. 练习或项目任务：至少 1 项，与本节知识点直接对应；
6. 本地作业（如有）：任务说明、起步代码、分步指引、常见报错、折叠答案；
7. 小结：3~5 条要点。

#### 3.3.3 各课小节与教学要点

| 课时 | 小节 | 教学要点 |
|-|-|-|
| L01 | 1.1 安装 Python 与验证 | 官网下载 3.10+；Windows 勾选 Add to PATH；`python --version` 验证 |
| L01 | 1.2 安装 VS Code 与第一个程序 | 安装 Python 扩展；新建 `hello.py`；运行按钮与终端运行 |
| L01 | 1.3 命令行运行与虚拟环境 | 终端、`python hello.py`、`python -m venv .venv`、激活脚本 |
| L01 | 1.4 pip 与依赖清单 | `pip install`、`pip list`、`pip freeze > requirements.txt`、安装失败排查 |
| L01 | 1.5 读 traceback 与常见报错 | 从下往上读报错、定位文件和行号、命令找不到、中文乱码、路径含空格 |
| L02 | 2.1 变量与赋值 | 命名规则、`=` 赋值、动态类型、命名习惯 |
| L02 | 2.2 基本数据类型 | `int`、`float`、`str`、`bool`、`None`；`type()` |
| L02 | 2.3 输入与输出 | `print()`、`input()` 返回字符串、`int()` 转换、f-string |
| L02 | 2.4 运算符与字符串 | 算术/比较/逻辑运算；拼接、索引、`len()`、`strip()` |
| L03 | 3.1 布尔值与比较 | `True`/`False`；比较运算；`and`/`or`/`not` |
| L03 | 3.2 if / elif / else | 缩进规则；多分支；成绩等级示例 |
| L03 | 3.3 while 循环 | 循环条件；计数器；死循环；`break` |
| L03 | 3.4 for 循环 | `range()`；遍历；`break`/`continue`；累加 |
| L04 | 4.1 定义与调用 | `def`；无参数/有参数函数；调用方式 |
| L04 | 4.2 参数与返回值 | 位置参数；默认参数；`return` |
| L04 | 4.3 作用域与标准库 | 局部/全局变量；`import math`、`import random` |
| L04 | 4.4 异常处理初识 | `try/except`；`ValueError`、`ZeroDivisionError`；详细见 L09 |
| L04 | 4.5 函数作为参数 | 函数是对象；把函数传入另一个函数；为工具注册做准备 |
| L05 | 5.1 列表基础 | 创建、索引、切片、修改、遍历 |
| L05 | 5.2 列表常用操作 | `append`、`insert`、`remove`、`pop`、`sort`、`in` |
| L05 | 5.3 字典基础 | 键值对、增删改查、`get()`、遍历 |
| L05 | 5.4 嵌套数据与元组/集合 | 列表套字典；字典套列表；元组不可变；集合去重 |
| L05 | 5.5 嵌套字典取值 | 多层键取值、`get()` 兜底、为 JSON 解析做准备 |
| L06 | 6.1 类与对象 | 类是模板、对象是实例；`class Student` |
| L06 | 6.2 属性与 `__init__` | 构造方法、`self`、实例属性 |
| L06 | 6.3 方法与封装 | 定义方法、调用方法、方法操作属性 |
| L06 | 6.4 为什么 Web 框架里有类 | `class Message(BaseModel)` 是固定写法；不展开继承原理 |
| L07 | 7.1 JSON 是什么 | 对象、数组、字符串、数字、布尔、`null`；与 Python 字典/列表的对应 |
| L07 | 7.2 `json.loads` 与 `json.dumps` | 字符串转对象、对象转字符串、`ensure_ascii=False`、`indent` |
| L07 | 7.3 文件读写 | `with open()`、`encoding="utf-8"`、`read`/`write`、`Path` |
| L07 | 7.4 编码、路径与常见错误 | 相对路径、文件不存在、编码错误、覆盖写入 |
| L07 | 7.5 小练习：解析与保存 | 解析 JSON 字段；写入文件再读回 |
| L08 | 8.1 URL、方法、状态码 | URL 组成、GET/POST、请求头、请求体、200/401/404/500 |
| L08 | 8.2 `requests.get` 与 `params` | 安装 `requests`、查询参数、`timeout`、`response.status_code` |
| L08 | 8.3 `requests.post` 与 JSON | `json=` 请求体、`headers`、Content-Type |
| L08 | 8.4 `response.json()` 与错误 | 解析响应、非 JSON 响应、超时与连接错误 |
| L08 | 8.5 真实 API 与 mock 接口 | 调用公开 API；使用平台 mock 接口做课堂练习 |
| L09 | 9.1 `try/except/else/finally` | 捕获指定异常；`else` 与 `finally`；异常链 |
| L09 | 9.2 捕获 requests 异常与重试 | `Timeout`、`ConnectionError`、`HTTPError`；简单重试与退出条件 |
| L09 | 9.3 `os.getenv` 与 `.env` | 环境变量、`python-dotenv`、`.env` 不提交 Git |
| L09 | 9.4 Key 安全、日志与轨迹 | 不硬编码 Key、日志脱敏、`logging` 记录每一步 |
| L09 | 9.5 小练习：失败重试与密钥读取 | 捕获异常并重试；从 `.env` 读取 Key |
| L10 | 10.1 数据库与表 | 表、行、列、主键；SQLite 单文件数据库 |
| L10 | 10.2 SQL 增删改查 | `CREATE TABLE`、`INSERT`、`SELECT`、`UPDATE`、`DELETE`、`WHERE`、`ORDER BY` |
| L10 | 10.3 Python 操作 SQLite | `sqlite3.connect`、`cursor`、`execute`、`commit`、`fetchall` |
| L10 | 10.4 参数化查询与留言表 | `?` 占位符、防 SQL 注入、`messages` 表设计 |
| L11 | 11.1 Web 请求与响应 | 浏览器 → HTTP 请求 → 服务器 → HTML；GET/POST；200/404/500 |
| L11 | 11.2 FastAPI 最小应用 | 安装 `fastapi`、`uvicorn`；`FastAPI()`；`@app.get("/")`；启动访问 |
| L11 | 11.3 Jinja2 模板 | `Jinja2Templates`、模板变量、静态文件 |
| L11 | 11.4 表单提交与写库 | `Form(...)`、POST 路由、调用数据库函数、重定向 |
| L11 | 11.5 留言列表与收尾 | 查询留言列表、模板循环、项目结构说明 |

#### 3.3.4 练习设计

| ID | 课时 | 题型 | 题目 | 输入/输出 | 考察点 |
|-|-|-|-|-|-|
| e01 | L01 | 单选 | 哪个命令可以查看 Python 版本 | 四选一 | 环境命令 |
| e02 | L01 | 编程 | 输出 `Hello, Python!` | 无输入 / 固定输出 | `print()`、运行程序 |
| e12 | L01 | 本地作业 | 搭好 Python 工作台 | 无自动判题 | venv、pip、运行脚本、读报错 |
| e03 | L02 | 填空 | 输出内容到控制台的函数是 ____ | 填 `print` | 输出函数 |
| e04 | L02 | 编程 | 两数求和 | 两行整数 / 一个整数 | `input()`、`int()`、运算 |
| e05 | L03 | 单选 | 判断循环输出结果 | 四选一 | `for`、`range` |
| e06 | L03 | 编程 | 判断奇偶 | 一个整数 / `偶数` 或 `奇数` | `if/else`、`%` |
| e07 | L03 | 编程 | 1 到 n 求和 | 正整数 / 一个整数 | 循环、累加 |
| e08 | L04 | 编程 | 求两数较大值 | 两行整数 / 一个整数 | 函数、参数、`return` |
| e13 | L04 | 编程 | 把函数当参数传 | 函数名 / 调用结果 | 函数对象、参数传递 |
| e09 | L05 | 编程 | 列表最大值与平均值 | 一行空格分隔整数 / 两行结果 | 列表、`max`、`sum`、格式化 |
| e14 | L05 | 编程 | 嵌套字典取值 | 嵌套字典 / 指定字段 | 多层取值、`get()` |
| e10 | L06 | 编程 | Student 类 | 姓名、成绩 / 及格结果 | `class`、`__init__`、方法 |
| e15 | L07 | 编程 | 解析 JSON 并输出字段 | 一行 JSON / `姓名:年龄` | `json.loads`、类型转换 |
| e16 | L07 | 编程 | 写入文件再读回 | 两行文本 / 行数与第一行 | `with open`、UTF-8、读写 |
| e17 | L08 | 编程 | 调用 mock 天气接口 | 城市名 / `城市 温度` | `requests.get`、`params`、`timeout`、`json()` |
| e18 | L08 | 本地作业 | 调用真实公开 API 并保存结果 | 无自动判题 | 真实网络、状态码、异常、写文件 |
| e19 | L09 | 编程 | 捕获除零异常 | 两个整数 / 结果或提示 | `try/except` |
| e20 | L09 | 编程 | 失败重试三次 | 无输入 / 成功或失败提示 | 异常捕获、循环重试、退出条件 |
| e21 | L09 | 本地作业 | 用 `.env` 管理 Key 并调用 API | 无自动判题 | 环境变量、Key 安全、请求头 |
| e11 | L10 | 编程 | SQLite 留言写入与查询 | 一行非空文本 / `已保存: 文本` | `sqlite3`、CRUD、参数化查询 |
| - | L11 | 项目任务 | 完成留言板并手动验收 | 无自动判题 | 路由、模板、表单、数据库 |

除 e02 固定输出题外，站内编程题每道 2~3 个用例，覆盖 0、负数、单元素等边界；输出比对按 5.7 规则执行。本地作业不设测试用例，提供参考答案与步骤说明，由学员自报完成。

#### 3.3.5 视觉内容安排

| 课时 | 组件 | 内容 |
|-|-|-|
| L01 | 概念卡 | Python 代码如何运行：源码 → 解释器 → 输出 |
| L02 | 概念卡 | 变量是贴标签的盒子 |
| L02 | 步骤动画 | 赋值与类型转换，3 步 |
| L03 | 对比卡 | `for` 与 `while` 的适用场景 |
| L03 | 步骤动画 | `for` 循环执行顺序，3~4 步 |
| L04 | 概念卡 | 函数是加工机器：输入 → 函数 → 返回值 |
| L05 | 概念卡 | 列表是有序抽屉，字典是带标签的柜子 |
| L06 | 概念卡 | 类是图纸，对象是房子 |
| L07 | 对比卡 | JSON 与 Python 字典的对应关系 |
| L07 | 步骤动画 | 文件读写三步：打开 → 读/写 → 关闭 |
| L08 | 概念卡 | 一次请求的旅程：客户端 → 服务端 → JSON 响应 |
| L08 | 步骤动画 | 一次 GET 请求的三步：发请求 → 判状态码 → 解析 JSON |
| L09 | 概念卡 | 异常处理流程：try → except → finally |
| L09 | 提示卡 | API Key 不能写进代码，也不能提交到 Git |
| L10 | 步骤动画 | 一条 `INSERT` 的执行过程，3 步 |
| L11 | 概念卡 | 浏览器 → FastAPI → SQLite → HTML 的完整旅程 |

#### 3.3.6 演示版内容深度

- 完整精写：L01–L03、L07–L09；
- 保留完整小节结构与示例：L04–L06、L10–L11；
- 11 节课都必须有正文和练习/项目任务入口，不允许空课；
- L11 不配置自动判题，正文给出项目任务清单，使用「标记完成」结束；
- 本地作业提供任务说明、起步代码与参考答案，不做自动检查；
- 站内编程题测试用例在学习页可展开查看，提交后按用例展示输入、期望与实际输出；
- 视觉素材优先完成 L02、L03、L07、L08、L09，其余可复用通用卡片模板；
- 内容生产与开发并行，M8 只做整合与补缺。

#### 3.3.7 内容依据

- Python 官方教程（中文）：`docs.python.org/zh-cn/3/tutorial/`
- Python `json` 文档：`docs.python.org/zh-cn/3/library/json.html`
- requests 官方文档：`requests.readthedocs.io/`
- python-dotenv 文档：`pypi.org/project/python-dotenv/`
- FastAPI 中文文档：`fastapi.tiangolo.com/zh/`
- SQLite 官方文档：`sqlite.org/docs.html`
- MDN HTTP 文档：`developer.mozilla.org/zh-CN/docs/Web/HTTP`
- Hello-Agents（Datawhale，CC BY-NC-SA 4.0）：作为 Agent 前置知识映射参考，只引用知识点与代码范式，不复制原文；每课底部标注对应章节；
- 若提供教材或教学大纲，按教材章节重新映射本大纲；不逐段复制教材原文；
- 所有代码示例必须在 Python 3.10+ 实际运行通过，版本相关 API 以官方文档为准。

---

## 4. 非功能需求

| 类别 | 要求 |
|-|-|
| 运行环境 | 本地：Windows 10/11 优先，兼容 macOS/Linux；Python 3.10 及以上；线上：Linux + Docker（可选）+ Caddy/Nginx + HTTPS |
| 依赖约束 | 本地不依赖 Node、Docker、PostgreSQL、Redis；线上仅判题沙箱使用 Docker；平台 Python 依赖为 8 个（基础 7 个 + HTTP 判题所需的 `requests`），课程示例额外使用 `python-dotenv` |
| 离线资源 | 图片、SVG、字体、动画脚本全部本地化；断网后课时页仍可完整显示 |
| 性能 | 本地页面响应小于 300ms；单用例判题超时 3 秒；站内题最多 3 个用例；支持 30 人以内同时使用；判题并发不超过 2 |
| 视觉性能 | 动画使用 CSS 过渡/位移实现，不引入 Canvas、WebGL 或重型动画脚本 |
| 安全 | 密码使用 PBKDF2-SHA256 加盐存储；会话 Cookie 设置 HttpOnly、SameSite=Lax，线上启用 Secure；所有 POST 增加 CSRF 校验；登录、注册、提交与 LLM 调用限流；学员 Key 加密存储、日志脱敏 |
| 安全边界 | 本地默认不暴露公网；线上部署必须启用 `JUDGE_MODE=docker` 或 `disabled`，并完成 HTTPS、CSRF 与限流加固；README 与 `DEPLOY.md` 明确声明「判题不是通用安全沙箱」 |
| 可用性 | 单进程启动；线上使用单 worker；异常退出后可重新启动；SQLite 数据文件持久化并定时备份 |
| 数据管理 | 数据文件位于 `data/app.db`；启用 WAL 与 `busy_timeout`；删除该文件即可重置全部数据；首次启动自动建表并写入演示账号 |
| 部署 | 提供 `Dockerfile`、`docker-compose.yml`、`Caddyfile`、`.env.example` 与 `DEPLOY.md`；`start.bat` 保留用于本地一键启动 |
| 兼容性 | 桌面端 Chrome / Edge 最近两个大版本 |
| 编码规范 | 全项目 UTF-8；中文内容不得出现乱码；所有文件路径使用 `pathlib` 处理 |
| 可维护性 | 课程内容与代码分离，修改课程只需编辑 `content/` 下文件并重启 |

---

## 5. 技术架构方案

### 5.1 技术栈定稿

| 层次 | 选型 | 版本/说明 |
|-|-|-|
| 开发语言 | Python | 3.10+ |
| Web 框架 | FastAPI | 提供页面路由与 JSON 接口 |
| ASGI 服务器 | Uvicorn | 本地启动 |
| 模板引擎 | Jinja2 | 服务端渲染 HTML |
| 前端 | 原生 HTML / CSS / JavaScript | 无构建步骤，静态资源全部本地化 |
| 视觉内容 | HTML 片段 + CSS 动画 + 原生 JS | 概念卡、对比卡、提示卡、分步动画，无第三方库 |
| 数据库 | SQLite | 零配置文件数据库 |
| ORM | SQLAlchemy 2.x | 同步 Session |
| Markdown 渲染 | Python-Markdown | 课时正文渲染 |
| 会话 | Starlette SessionMiddleware + itsdangerous | 签名 Cookie |
| 密码哈希 | hashlib.pbkdf2_hmac | 标准库，不引入 passlib |
| 判题 | subprocess / Docker | 本地用 subprocess；线上用 Docker 隔离，按 `JUDGE_MODE` 切换 |
| 在线部署 | Docker + Caddy | 可选；Caddy 负责 TLS 与反向代理 |
| 启动方式 | `python run.py` / `start.bat` | 本地自动建库并启动服务 |

> 平台判题环境需要 `requests`（用于 e17 的 mock HTTP 题）；课程示例额外使用 `python-dotenv`，由学员在自己的虚拟环境安装。

**为什么这样选：**

1. **运行成本最低**：一个 Python 环境 + 一条 `pip install` + 一条启动命令，没有 Docker 和 Node。
2. **前端就是三大件**：Jinja2 输出 HTML，CSS/JS 为本地静态文件，判题提交用原生 `fetch`，不需要前端框架和构建链。
3. **FastAPI 足够轻**：路由清晰、表单与 JSON 处理方便、AI 生成代码不易出错；本项目不需要 Django 的后台与 ORM 全家桶。
4. **SQLite 零配置**：数据量小、单机使用，删库文件即可重置，适合演示。
5. **内容文件化**：课程用 Markdown + JSON 维护，省掉内容管理后台这一整块工作量。

### 5.2 架构说明

```
浏览器（HTML/CSS/JS）
        │  HTTP / HTTPS
        ▼
Caddy（可选，线上 TLS 与反向代理）
        │
        ▼
FastAPI 应用（Jinja2 服务端渲染 + JSON 接口）
        │
        ├── SQLite（用户、学习进度，WAL）
        │
        ├── ContentLoader（启动时读取 content/ 并校验）
        │
        └── JudgeService
              ├── JUDGE_MODE=subprocess（本地）
              ├── JUDGE_MODE=docker（线上，隔离）
              └── mock_http 夹具（HTTP 类站内题）
```

- 页面请求走服务端渲染，返回完整 HTML；
- 练习提交走 `fetch` 调用 JSON 接口，前端只负责展示结果；
- 判题接口使用同步 `def` 路由，由 FastAPI 线程池执行，避免阻塞事件循环；
- 本地作业不进入判题服务，只写完成状态；
- 课程内容在启动时一次性加载进内存，运行期只读。

### 5.3 目录结构

```
Programming Learning Guide/
├── app/
│   ├── __init__.py
│   ├── main.py                 # 应用入口、路由注册、中间件
│   ├── config.py               # 路径、常量、端口配置
│   ├── db.py                   # 引擎、Session、建表、初始化
│   ├── models.py               # SQLAlchemy 模型
│   ├── auth.py                 # 密码哈希、登录态依赖
│   ├── content.py              # 课程加载与校验
│   ├── judge.py                # 判题服务
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── pages.py            # 页面路由
│   │   ├── auth_routes.py      # 注册/登录/退出
│   │   └── api.py              # 练习提交、进度接口
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── roadmap.html
│   │   ├── lesson.html
│   │   └── _exercise_preview.html
│   └── static/
│       ├── style.css
│       ├── app.js
│       └── img/
│           ├── python-flow.svg
│           ├── var-box.svg
│           ├── step-1.svg
│           ├── step-2.svg
│           ├── json-dict.svg        # v2：JSON 与字典
│           ├── file-io.svg          # v2：文件读写
│           ├── http-journey.svg     # v2：请求-响应
│           ├── exception-flow.svg   # v2：异常流程
│           └── key-safety.svg       # v2：Key 安全
├── content/
│   ├── course.json             # 课程结构
│   ├── exercises.json          # 练习配置
│   └── lessons/
│       ├── l01.md
│       ├── l02.md
│       ├── ...
│       ├── l07.md              # JSON 与文件读写
│       ├── l08.md              # HTTP 与真实 API
│       ├── l09.md              # 异常、环境变量与密钥
│       ├── l10.md              # SQLite（原 l07）
│       └── l11.md              # FastAPI（原 l08）
├── deploy/                     # v2 规划
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── Caddyfile
├── data/
│   ├── app.db                  # 运行时生成
│   └── secret_key              # 运行时生成
├── requirements.txt
├── .env.example                # v2 规划：环境变量模板
├── run.py                      # 启动脚本
├── start.bat                   # Windows 一键启动
├── DEPLOY.md                   # v2 规划
└── README.md
```

### 5.4 数据模型

#### users

| 字段 | 类型 | 约束 |
|-|-|-|
| id | INTEGER | 主键自增 |
| username | TEXT | 唯一、非空 |
| password_hash | TEXT | 非空，格式 `pbkdf2_sha256$迭代次数$盐$哈希` |
| created_at | TEXT | ISO 时间字符串 |

#### lesson_progress

| 字段 | 类型 | 约束 |
|-|-|-|
| id | INTEGER | 主键自增 |
| user_id | INTEGER | 外键 users.id |
| lesson_id | TEXT | 课程文件中的课时 ID |
| status | TEXT | `completed` / 未记录视为未开始 |
| updated_at | TEXT | ISO 时间字符串 |

唯一约束：`(user_id, lesson_id)`。

#### exercise_progress

| 字段 | 类型 | 约束 |
|-|-|-|
| id | INTEGER | 主键自增 |
| user_id | INTEGER | 外键 users.id |
| exercise_id | TEXT | 练习 ID |
| status | TEXT | 站内题：`accepted` / `wrong_answer` / `timeout` / `runtime_error`；本地作业：`accepted` 表示已完成 |
| attempts | INTEGER | 提交次数，内部统计，界面不展示 |
| last_answer | TEXT | 最新一次作答内容：选项索引、填空答案或代码；本地作业置空，可为空 |
| updated_at | TEXT | ISO 时间字符串 |

唯一约束：`(user_id, exercise_id)`。

> v2 不新增表。`local_task` 完成时写入 `exercise_progress.status = accepted`，`last_answer` 置空；本地作业不保存提交内容。

### 5.5 页面与路由清单

| 方法 | 路径 | 说明 | 登录要求 |
|-|-|-|-|
| GET | `/` | 已登录跳 `/roadmap`，未登录跳 `/login` | 否 |
| GET | `/login` | 登录页 | 否 |
| POST | `/login` | 处理登录表单 | 否 |
| GET | `/register` | 注册页 | 否 |
| POST | `/register` | 处理注册表单，成功后自动登录 | 否 |
| POST | `/logout` | 退出并清除会话 | 是 |
| GET | `/roadmap` | 学习路线页 | 是 |
| GET | `/lessons/{lesson_id}` | 课时页，含正文与练习 | 是 |
| POST | `/api/exercises/{exercise_id}/submit` | 提交练习并返回判题结果（仅单选/填空/站内编程） | 是 |
| POST | `/api/exercises/{exercise_id}/complete` | 本地作业标记完成 | 是 |
| GET | `/mock/http/{name}` | 教学用固定响应接口，返回 mock JSON | 否 |
| POST | `/api/lessons/{lesson_id}/complete` | 无练习课时的标记完成 | 是 |

### 5.6 接口契约

#### POST /api/exercises/{exercise_id}/submit

请求体（按题型区分）：

```json
// 单选题
{ "answer_index": 1 }

// 填空题
{ "answer": "print" }

// 编程题
{ "code": "print('Hello, World!')" }
```

成功响应：

```json
{
  "status": "accepted",
  "message": "全部测试用例通过",
  "expected": "",
  "actual": "",
  "duration_ms": 120,
  "lesson_completed": true,
  "progress_percent": 20
}
```

失败响应示例：

```json
{
  "status": "wrong_answer",
  "message": "第 1 个测试用例输出不一致",
  "expected": "Hello, World!",
  "actual": "Hello",
  "duration_ms": 98,
  "lesson_completed": false,
  "progress_percent": 0
}
```

错误码：

| HTTP 状态 | 场景 |
|-|-|
| 401 | 未登录 |
| 403 | CSRF 校验失败，或线上关闭了编程判题 |
| 404 | 练习或课时不存在 |
| 422 | 请求体缺失或类型错误 |
| 429 | 提交过于频繁 |
| 500 | 判题服务内部错误，返回 `status: internal_error`，不写入 `exercise_progress` |

#### POST /api/exercises/{exercise_id}/complete

请求体：无，或 `{}`。仅用于 `local_task`，不接收代码或文件。

成功响应：

```json
{
  "status": "accepted",
  "message": "本地作业已完成",
  "lesson_completed": true,
  "progress_percent": 36
}
```

错误码：

| HTTP 状态 | 场景 |
|-|-|
| 400 | 该练习不是 `local_task` |
| 401 | 未登录 |
| 404 | 练习不存在 |

规则：幂等；已完成重复调用返回 200；允许「重新练习」后再次标记完成。`local_task` 不走 `submit` 接口。

### 5.7 判题实现规范

1. 在 `data/tmp/` 下创建唯一临时目录，写入 `main.py`；
2. 使用 `sys.executable -I -X utf8 main.py` 启动子进程，`cwd` 为临时目录；
3. 测试用例的 `stdin` 通过管道传入；
4. 单用例超时 3 秒，超时后终止子进程并返回 `timeout`；
5. 退出码非 0 返回 `runtime_error`，附带截断后的 stderr；
6. 退出码为 0 时按规则比对 stdout；
7. 每个用例执行后清理临时目录；
8. 环境变量继承当前进程；使用 `-X utf8` 启用 UTF-8 模式，子进程输出按 UTF-8 解码（`-I` 会忽略 `PYTHON*` 环境变量，因此不再依赖 `PYTHONIOENCODING`）；
9. 返回的 `expected`、`actual`、`stderr` 均截断至 2000 字符；
10. 判题接口声明为同步 `def`，交给 FastAPI 线程池执行；
11. `mock_http` 夹具：为 HTTP 类站内题在隔离环境内启动本地 mock 服务，绑定 `127.0.0.1`，返回固定 JSON；学员代码通过 `MOCK_BASE_URL` 或固定端口访问，不依赖外网；
12. `JUDGE_MODE`：支持 `subprocess`（本地）、`docker`（线上一容器一用例）与 `disabled`（关闭编程判题）；`docker` 模式限制网络、内存、CPU、PID，只读根目录，非 root；
13. 本地作业不进入判题服务，只写完成状态。

输出比对函数：

```python
def normalize_output(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines).strip("\n")
```

**边界声明**：subprocess 判题不是安全沙箱，不隔离网络、文件与进程，仅用于本地课程演示；线上部署必须使用 `JUDGE_MODE=docker` 或 `JUDGE_MODE=disabled`，README 与 `DEPLOY.md` 必须明确写出这一点。

### 5.8 内容文件格式

#### course.json

```json
{
  "course_title": "Python 从零到 Web 应用 · Agent 先修",
  "stages": [
    {
      "id": "s1",
      "title": "第一章：环境配置",
      "lesson_ids": ["l01"]
    }
  ],
  "lessons": [
    {
      "id": "l01",
      "stage_id": "s1",
      "title": "安装 Python 并运行第一个程序",
      "content_file": "lessons/l01.md",
      "exercise_ids": ["e01", "e02", "e12"]
    }
  ]
}
```

#### exercises.json

以下为字段结构示例；正式题目、测试用例与 ID 以 3.3.4 和内容模块为准。文件 ID 使用小写，页面显示为大写。

```json
[
  {
    "id": "e01",
    "lesson_id": "l01",
    "type": "single_choice",
    "title": "下面哪个命令可以查看 Python 版本？",
    "options": ["python --version", "python run", "pip install", "python help"],
    "answer_index": 0,
    "explanation": "`python --version` 用于查看当前 Python 版本。"
  },
  {
    "id": "e02",
    "lesson_id": "l02",
    "type": "fill_blank",
    "title": "输出内容到控制台的函数是 ____。",
    "answers": ["print"],
    "case_sensitive": false,
    "explanation": "Python 使用 print() 输出内容。"
  },
  {
    "id": "e03",
    "lesson_id": "l01",
    "type": "coding",
    "title": "输出 Hello, Python!",
    "description": "编写程序，在标准输出中打印 Hello, Python!",
    "starter_code": "print(\"Hello\")",
    "timeout_seconds": 3,
    "test_cases": [
      {
        "stdin": "",
        "expected_stdout": "Hello, Python!"
      }
    ]
  }
]
```

**本地作业（`local_task`）字段示例**

```json
{
  "id": "e12",
  "lesson_id": "l01",
  "type": "local_task",
  "title": "搭好 Python 工作台",
  "description": "创建虚拟环境、安装 requests，并运行脚本输出 requests 版本。",
  "steps": [
    "在项目目录执行 `python -m venv .venv`",
    "激活虚拟环境",
    "执行 `pip install requests`",
    "新建 `check.py`，打印 `requests.__version__`",
    "在终端运行 `python check.py`"
  ],
  "starter_code": "import requests\n\nprint(requests.__version__)\n",
  "answer": "先创建并激活虚拟环境，再安装依赖，最后运行脚本。",
  "answer_code": "python -m venv .venv\n.venv\\Scripts\\activate\npip install requests\npython check.py",
  "common_errors": [
    "提示 `python` 不是内部或外部命令：检查 PATH",
    "激活脚本被系统策略拦截：改用 `.venv\\Scripts\\python.exe` 直接运行"
  ]
}
```

`local_task` 不配置 `test_cases`，不需要 `timeout_seconds`；平台只渲染任务卡、步骤、答案与「标记完成」按钮，不执行代码。

#### 视觉卡片与步骤动画

课时正文使用 Markdown，允许在正文中内嵌以下固定 HTML 片段。HTML 片段前后必须留空行；样式由 `app/static/style.css` 提供，交互由 `app/static/app.js` 统一绑定。正文中禁止出现 `<script>`、内联事件或外部资源。

**概念卡**

```html
<div class="v-card">
  <img class="v-card-img" src="/static/img/var-box.svg" alt="变量是带标签的盒子">
  <div class="v-card-body">
    <h4>变量是带标签的盒子</h4>
    <p>变量名是标签，值是盒子里的内容。赋值就是把内容放进盒子。</p>
  </div>
</div>
```

**对比卡**

```html
<div class="v-compare">
  <div class="v-compare-item is-wrong">
    <h4>错误</h4>
    <p>print("Hello")</p>
  </div>
  <div class="v-compare-item is-right">
    <h4>正确</h4>
    <p>print("Hello, World!")</p>
  </div>
</div>
```

**提示卡**

```html
<div class="v-callout is-tip">
  <strong>记忆技巧</strong>
  <p>变量名尽量使用有意义的英文单词，例如 age、name、total。</p>
</div>
```

**步骤动画**

```html
<div class="step-player">
  <div class="step is-active">
    <p>第 1 步：创建一个空盒子，贴上标签 age。</p>
    <img src="/static/img/step-1.svg" alt="创建变量 age">
  </div>
  <div class="step">
    <p>第 2 步：把 18 放进盒子里。</p>
    <img src="/static/img/step-2.svg" alt="age 赋值为 18">
  </div>
  <div class="step-controls">
    <button type="button" data-action="prev">上一步</button>
    <span class="step-indicator">1 / 2</span>
    <button type="button" data-action="next">下一步</button>
    <button type="button" data-action="replay">重播</button>
  </div>
</div>
```

**视觉组件规则**

- `app.js` 用事件委托绑定所有 `.step-player`，不为单个课时写脚本；
- 同一容器内只显示带 `.is-active` 的 `.step`；
- 首步禁用「上一步」，末步禁用「下一步」；
- 指示器显示 `当前步 / 总步数`；
- 「重播」将当前步重置为第 1 步；
- 每篇课时最多 2 个步骤动画，单个动画 2~4 步；
- 图片统一放在 `app/static/img/`，优先 SVG，必须填写 `alt`；
- 卡片与动画的样式只使用固定类名，不在正文中写样式。

#### 启动时校验规则

加载失败必须抛出明确错误并终止启动，错误信息包含文件路径与原因：

- 阶段 ID、课时 ID、练习 ID 全局唯一；
- 阶段的 `lesson_ids` 必须存在；
- 课时的 `stage_id` 必须存在；
- `content_file` 必须存在且可读；
- 课时的 `exercise_ids` 必须存在；为空时该课时使用「标记完成」，非空时每个练习必须存在且 `lesson_id` 与课时一致；
- 单选题 `answer_index` 必须在选项范围内；
- 站内编程题至少有一个测试用例；
- `local_task` 必须有 `description`、`steps`、`answer`，且不配置 `test_cases`；
- `mock_http` 题必须声明 mock 路径与固定响应。

### 5.9 启动与运行方式

README 中的标准步骤（Windows）：

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

浏览器访问 `http://127.0.0.1:8000`。

`run.py` 的职责：

1. 创建 `data/` 目录；
2. 若 `data/secret_key` 不存在则生成并保存，保证重启后会话仍有效；
3. 创建数据库表；
4. 若演示账号不存在则写入 `demo / demo123`；
5. 启动 Uvicorn，监听 `127.0.0.1:8000`，端口可通过环境变量 `PORT` 覆盖；
6. 控制台打印访问地址。

`start.bat` 的职责：检测虚拟环境是否存在，不存在则创建并安装依赖，然后启动 `run.py`。

**线上部署（v2 规划）**

1. 复制 `.env.example` 为 `.env`，固定写入 `APP_SECRET_KEY`、`DATABASE_URL`、`HTTPS_ONLY=true`、`JUDGE_MODE=docker`；
2. `docker compose up -d` 启动 app 与 Caddy；
3. Caddy 自动申请 HTTPS 证书并反向代理到 app；
4. `data/` 挂载持久卷，配置每日备份；
5. `/health` 接入监控；
6. 详见 `DEPLOY.md`。

线上环境变量：

| 变量 | 说明 |
|-|-|
| `APP_ENV` | `local` / `production`；生产必须固定 `APP_SECRET_KEY` |
| `APP_SECRET_KEY` | 生产必须固定注入，不使用 `data/secret_key` 自动生成 |
| `DATABASE_URL` | 默认 `sqlite:///data/app.db` |
| `HTTPS_ONLY` | 线上 `true`，启用 Secure Cookie 与 HSTS |
| `TRUST_PROXY` | 在 Caddy/Nginx 后设为 `true`，限流按 `X-Forwarded-For` 取 IP |
| `JUDGE_MODE` | `subprocess` / `docker` / `disabled` |
| `JUDGE_DOCKER_IMAGE` | 判题镜像，默认 `plg-judge:latest` |
| `JUDGE_CONCURRENCY` | 判题并发，默认 2，范围 1~4 |
| `DOCKER_BIN` | Docker CLI 路径，默认 `docker` |

### 5.10 技术风险与边界

| 风险 | 说明 | 应对 |
|-|-|-|
| 判题无真实沙箱 | 学生代码可读写本地文件、访问网络 | 本地用 subprocess 并明确边界；线上用 `JUDGE_MODE=docker` 或 `disabled` |
| 公网判题被滥用 | 任意代码执行、资源耗尽 | Docker 限制网络/内存/CPU/PID、只读根目录、非 root；判题并发限 2 |
| Key 泄露 | 学员 Key 进入日志或代码 | 加密存储、日志脱敏、界面隐藏；禁止在课程正文出现真实 Key |
| 网络与 API 成本 | 超时、限流、费用失控 | 练习用录制回放；真实 API 设超时、重试上限与每日配额 |
| 本地作业自报 | 进度可信度下降 | 30 人以内抽查；后续用轨迹 JSON 规则检查 |
| 死循环占资源 | 用户提交死循环代码 | 3 秒超时并终止子进程 |
| Windows 编码问题 | 控制台默认编码导致中文乱码 | 子进程使用 `-X utf8`；所有文件 UTF-8 |
| 端口被占用 | 8000 端口冲突 | 支持 `PORT` 环境变量；README 提供排查说明 |
| 依赖安装失败 | 验收环境网络受限 | 依赖数量控制在 8 个以内；README 提供离线安装说明 |
| 会话丢失 | 重启后 secret 变化 | 本地持久化到 `data/secret_key`；线上固定注入 `APP_SECRET_KEY` |
| 视觉组件失效 | 图片外链或第三方库在验收环境不可用 | 图片、CSS、JS 全部本地；验收清单包含断网检查 |

---

## 6. 项目里程碑

> 以下按 14 天排期。若实践周更短，按阶段顺序压缩，优先保证功能清单全部完成。

| 阶段 | 时间 | 交付物 | 完成标准 |
|-|-|-|-|
| M1 项目骨架 | D1–D2 | 项目结构、数据库模型、建表与初始化、`run.py` | 已完成 |
| M2 账号体系 | D3 | 注册、登录、退出、会话中间件 | 已完成 |
| M3 课程链路 | D4–D5 | ContentLoader、路线页、课时页、Markdown 渲染、视觉组件渲染 | 已完成 |
| M4 练习判题 | D6–D7 | 概念题判定、判题服务、练习提交接口、结果展示 | 已完成 |
| M5 进度体系 | D8 | 练习进度、课时完成、路线完成度、上下课导航 | 已完成 |
| M6 演示内容 | D9–D10 | 8 课正文、11 道练习、视觉素材 | 已完成（v1.0） |
| M7 交付验收 | D11–D14 | README、`start.bat`、验收记录、截图 | 已完成（2026-10-29） |
| M8 Agent 先修内容 | 2026-11-03 | L07–L09 正文、10 道练习、`local_task` 题型、mock HTTP | 已完成：11 课可打开；21 道练习可提交或标记完成 |
| M9 上线加固 | 2026-11-03 | CSRF、HTTPS、限流、WAL、安全响应头 | 已完成：POST 带 CSRF、6 次失败登录 429、响应头与 WAL 验证通过 |
| M10 部署交付 | 2026-11-03 | Dockerfile、compose、Caddy、`DEPLOY.md`、Docker 判题 | 产物已完成；容器启动与 HTTPS 待部署服务器验证 |

### 6.1 交付物清单

- 可运行的完整源码；
- `requirements.txt`；
- `README.md`（环境要求、安装、启动、演示账号、常见问题）；
- `start.bat`；
- `content/` 中的 6 章 11 课内容、21 道练习（18 道站内 + 3 道本地作业）与 1 个项目任务；
- v2 部署材料：`Dockerfile`、`docker-compose.yml`、`Caddyfile`、`.env.example`、`DEPLOY.md`（规划）；
- 已执行的验收清单（可写在 README 末尾）。

---

## 7. 风险评估与应对

| 风险 | 概率 | 影响 | 应对措施 |
|-|-|-|-|
| 范围膨胀，核心功能做不完 | 高 | 高 | 严格按功能清单开发，不增加清单外的功能 |
| 判题功能调试耗时超预期 | 中 | 高 | 先实现「单用例 + 正确/错误」最小闭环，再补超时与多用例 |
| 验收电脑环境不兼容 | 中 | 高 | 明确 Python 3.10+；依赖最少化；在干净环境完整走一遍安装流程 |
| 内容量不足，演示不完整 | 中 | 中 | 路线骨架必须完整；正文优先保证 11 篇；练习覆盖站内与本地两类 |
| 视觉素材制作耗时 | 中 | 中 | 优先使用可复用 SVG 简笔图与统一卡片模板，3~5 个素材覆盖多篇课时 |
| 中文乱码 | 中 | 中 | 全项目 UTF-8；子进程设置编码；模板声明 charset |
| SQLite 并发写入冲突 | 低 | 低 | 30 人以内；单 worker、WAL、短事务 |
| 会话重启失效 | 低 | 中 | 本地 secret 持久化；线上固定注入 `APP_SECRET_KEY` |
| 本地作业流于形式 | 中 | 中 | 提供参考答案与常见报错；30 人以内抽查；不把完成度当考核依据 |
| 公网判题被滥用 | 中 | 高 | 上线前完成 Docker 隔离与限流；无法隔离时关闭编程判题 |
| API Key 泄露 | 中 | 高 | 加密存储、日志脱敏；课程中只出现占位 Key |
| 网络不稳定导致学员卡住 | 高 | 中 | 提供 mock 接口与常见报错；真实 API 任务允许换服务 |

---

## 8. 验收清单

> v1.0 验收结果记录见 `docs/验收记录.md`（2026-10-29，全部通过）。v2.0 验收待开发完成后补充。

验收者按以下顺序检查，全部通过即验收完成：

- [ ] 按 README 完成安装，`python run.py` 启动成功；
- [ ] 浏览器打开 `http://127.0.0.1:8000`，跳转到登录页；
- [ ] 使用 `demo / demo123` 登录成功；
- [ ] 注册一个新账号，注册后自动登录；
- [ ] 路线页显示 6 个章节、11 节课与完成度；
- [ ] 点击「继续学习」进入第一个未完成课时；
- [ ] 课程共 6 章 11 课，11 节课均可打开；
- [ ] 课时正文 Markdown 渲染正确，代码块显示正常；
- [ ] 课时页展示视觉卡片，图片正常、布局正确；
- [ ] 步骤动画支持上一步、下一步、重播，指示器显示正确；
- [ ] 断开网络后刷新，卡片与动画仍正常显示；
- [ ] 单选题答对返回通过，答错返回错误并显示解析；
- [ ] 填空题大小写与首尾空格不影响判定；
- [ ] L01–L10 的站内编程题均可提交并正确判题；
- [ ] L08 的 mock HTTP 题可提交并通过，不依赖外网；
- [ ] 编程题提交正确代码返回「通过」；
- [ ] 提交错误代码返回「答案错误」，并显示期望与实际输出；
- [ ] 提交 `while True: pass` 返回「超时」，且不超过 3 秒；
- [ ] 提交 `1/0` 返回「运行错误」；
- [ ] L01、L08、L09 的本地作业可查看任务、步骤与折叠答案；
- [ ] 点击「标记完成」后本地作业显示已完成，可「重新练习」；
- [ ] 完成该课全部练习（含本地作业）后，课时变为已完成；
- [ ] 返回路线页，完成度百分比更新；
- [ ] 刷新页面与重启服务后，账号与进度仍在；
- [ ] L11 可按项目任务完成留言板，并使用「标记完成」结束课时；
- [ ] 本地运行全程未依赖外网 CDN、Node、Docker；
- [ ] 登录页、注册页含 CSRF 隐藏字段，页面 meta 含 `csrf-token`；
- [ ] 不带 CSRF 的登录 POST 返回 403；
- [ ] 带 CSRF 的登录、练习提交、本地作业完成成功；
- [ ] 连续 6 次错误登录，第 6 次返回 429；
- [ ] 响应头包含 `X-Content-Type-Options`、`X-Frame-Options`、`Content-Security-Policy`；
- [ ] SQLite 为 WAL 模式，`busy_timeout=5000`；
- [ ] `JUDGE_MODE=disabled` 时编程题显示提示且提交返回 403；
- [ ] `APP_ENV=production` 且缺少 `APP_SECRET_KEY` 时启动失败；
- [ ] 线上部署按 `DEPLOY.md` 启动，HTTPS 可访问（待部署服务器验证）；
- [ ] 线上 `JUDGE_MODE=docker` 或 `disabled`，未使用不隔离的 subprocess 判题（待部署服务器验证）；
- [ ] `deploy/Dockerfile`、`judge.Dockerfile`、`docker-compose.yml`、`Caddyfile` 存在且结构正确；
- [ ] `JUDGE_MODE=docker` 命令包含 `--network none`、内存/CPU/PID 限制、只读根目录与非 root。

---

## 附录 A：AI 开发约束（必须遵守）

**必须：**

- 使用 Python 3.10+ 可运行的语法；
- 所有页面服务端渲染，静态资源放在 `app/static/`；
- 所有路径使用 `pathlib`，不使用硬编码绝对路径；
- 所有文件 UTF-8 编码；
- 平台依赖仅限：`fastapi`、`uvicorn`、`jinja2`、`sqlalchemy`、`python-multipart`、`itsdangerous`、`markdown`、`requests`；
- 课程示例可要求学员安装 `python-dotenv`；平台判题需要 `requests`；
- 数据库与判题相关路由使用同步 `def`；
- 视觉组件使用固定 CSS 类名，图片使用 `app/static/img/` 下的本地文件；
- 步骤动画用原生 JS 实现，禁止第三方动画库；
- 错误信息必须具体到文件与原因；
- README 必须包含安全边界声明；
- `local_task` 不执行代码、不保存提交内容，只写完成状态；
- 所有 POST 必须校验 CSRF；线上部署必须启用 HTTPS、限流与安全响应头；
- 生产环境必须固定注入 `APP_SECRET_KEY`。

**禁止：**

- 本地运行引入 Node、npm、Docker、Redis、Celery、PostgreSQL；线上判题沙箱使用 Docker 不属于此限制；
- 引入 React/Vue 等前端框架或构建步骤；
- 使用外网 CDN、在线字体、在线图标；
- 在课程正文中写 `<script>` 或内联事件；
- 引用外链图片、视频、在线字体或图标库；
- 存储明文密码；
- 在 `local_task` 中执行学员代码；
- 在日志中打印学员 API Key；
- 关闭 CSRF 校验或限流；
- 在未启用 HTTPS 的情况下把 `APP_ENV` 设为 `production`；
- 假设本地默认部署到公网。

---

## 附录 B：版本记录

| 版本 | 日期 | 说明 |
|-|-|-|
| v2.2 | 2026-11-03 | M10 部署产物：Dockerfile、judge.Dockerfile、compose、Caddyfile、DEPLOY.md 与 Docker 判题 |
| v2.1 | 2026-11-03 | M9 上线加固：CSRF、限流、HTTPS 配置、安全响应头、WAL 与 `JUDGE_MODE=disabled` |
| v2.0 | 2026-11-03 | Agent 先修扩展：6 章 11 课、21 道练习、`local_task` 题型、mock HTTP 判题、上线部署规划 |
| v1.0 | 2026-10-26 | 初版：5 章 8 课、11 道练习、M1–M7 交付验收 |
