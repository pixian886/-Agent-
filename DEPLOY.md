# 《从零开始Agent学习》部署说明（M10）

> 目标：在一台 Linux 云服务器上，用 Docker Compose 启动 FastAPI 应用、Caddy 反向代理与隔离判题容器。
> 本地开发仍然使用 `python run.py` / `start.bat`，不受本文影响。

---

## 1. 部署架构

```text
浏览器
  │ HTTPS
  ▼
Caddy（80/443，自动证书）
  │ 反向代理
  ▼
app 容器（FastAPI + Docker CLI）
  ├── SQLite（/app/data/app.db，持久卷）
  ├── content/（课程文件）
  └── docker run（宿主机 Docker）
        └── plg-judge 容器（--network none、内存/CPU/PID 限制、只读根目录、非 root）
```

- `app` 容器通过挂载 `/var/run/docker.sock` 调用宿主机 Docker；
- 判题容器每次执行一个测试用例，执行完自动删除；
- `data/` 挂载到宿主机，重启容器不丢数据；
- Caddy 负责 HTTPS 证书与反向代理。

> **安全警告**：挂载 Docker socket 等于把宿主机 Docker 控制权交给 `app` 容器。只在你信任的服务器上使用；如果无法接受，把 `JUDGE_MODE` 改为 `disabled`，并移除 socket 挂载。`disabled` 会关闭站内编程判题，只保留选择、填空与本地作业。

---

## 2. 前置条件

- Linux 云服务器，建议 2 核 2G 以上；
- Docker Engine 24+；
- Docker Compose v2.17+（需要 `service_completed_successfully`）；
- 一个域名，A 记录指向服务器；
- 服务器防火墙开放 80、443；不要暴露 8000；
- 服务器能访问 Docker Hub（拉取 `python:3.12-slim`、`caddy:2`）。

检查：

```bash
docker --version
docker compose version
```

---

## 3. 首次部署

### 3.1 上传项目

把项目目录传到服务器，排除 `.venv/`、`data/`、`__pycache__/`。可以使用 `scp`、`rsync` 或 Git。

```bash
cd /opt/programming-learning-guide
```

### 3.2 生成 `.env`

```bash
cp deploy/.env.example .env
```

编辑 `.env`：

```bash
DOMAIN=your-domain.example.com
APP_ENV=production
APP_SECRET_KEY=<随机值>
HTTPS_ONLY=true
TRUST_PROXY=true
JUDGE_MODE=docker
JUDGE_DOCKER_IMAGE=plg-judge:latest
JUDGE_CONCURRENCY=2
DATABASE_URL=sqlite:////app/data/app.db
```

生成 `APP_SECRET_KEY`：

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

> `APP_SECRET_KEY` 一旦上线就不要随意更换，否则所有登录态会失效。

### 3.3 构建镜像

```bash
docker compose -f deploy/docker-compose.yml build
```

这会构建：

- `plg-app:latest`：应用镜像，包含 Docker CLI；
- `plg-judge:latest`：判题镜像，包含 Python 与 `requests`。

### 3.4 启动

```bash
docker compose -f deploy/docker-compose.yml up -d
```

查看状态：

```bash
docker compose -f deploy/docker-compose.yml ps
docker compose -f deploy/docker-compose.yml logs -f app caddy
```

### 3.5 验证

```bash
curl -I https://your-domain.example.com/health
```

浏览器打开域名，使用 `demo / demo123` 登录，或注册新账号。

重点检查：

- 登录、注册表单能正常提交（CSRF 生效）；
- 连续错误登录第 6 次返回 429；
- 提交站内编程题能看到判题结果；
- `docker ps` 在提交期间能看到短暂的 `plg-judge-...` 容器；
- 刷新页面后进度保留；
- 重启 `app` 容器后账号与进度仍在。

---

## 4. 判题容器说明

应用以 `JUDGE_MODE=docker` 启动时，每个测试用例执行：

```text
docker run --rm -i
  --network none
  --memory 128m --memory-swap 128m
  --cpus 0.5 --pids-limit 64
  --read-only
  --tmpfs /work:rw,exec,nosuid,size=16m,mode=1777
  -v <临时目录>:/src:ro
  -w /work
  --user 65534:65534
  --cap-drop ALL
  --security-opt no-new-privileges
  --pull=never
  plg-judge:latest
  sh -c "cp /src/main.py /work/main.py && timeout 3 python -I -B -X utf8 /work/main.py"
```

- `--network none`：学员代码不能访问外网；
- `--read-only` + `/work` tmpfs：根目录只读，可写空间 16MB；
- 非 root、丢弃 capability；
- `timeout 3`：容器内限时，外层还有 5 秒兜底；
- `--pull=never`：避免判题时临时拉镜像；镜像缺失会直接返回运行错误。

HTTP 类题（e17）会把 `sandbox_runner.py` 和 `mock_config.json` 复制进容器，在容器内启动 `127.0.0.1:8765` 的 mock 服务，学员代码请求本地地址。

---

## 5. 日常运维

### 5.1 日志

```bash
docker compose -f deploy/docker-compose.yml logs -f app
docker compose -f deploy/docker-compose.yml logs -f caddy
```

### 5.2 备份

SQLite 开了 WAL，直接复制 `app.db` 可能漏掉 `-wal` 内容。推荐用 SQLite 在线备份：

```bash
docker compose -f deploy/docker-compose.yml exec app python -c \
"import sqlite3; src=sqlite3.connect('/app/data/app.db'); dst=sqlite3.connect('/app/data/backup.db'); src.backup(dst); dst.close(); src.close()"
cp data/backup.db /backup/app-$(date +%F).db
```

也可以停止 `app` 后复制整个 `data/`。

### 5.3 升级

```bash
git pull
docker compose -f deploy/docker-compose.yml build
docker compose -f deploy/docker-compose.yml up -d
```

### 5.4 重启与停止

```bash
docker compose -f deploy/docker-compose.yml restart app
docker compose -f deploy/docker-compose.yml down
```

`down` 不会删除 `data/` 与 Caddy 证书卷。

---

## 6. 常见问题

| 现象 | 排查 |
|-|-|
| Caddy 申请证书失败 | 域名 A 记录是否正确；80/443 是否开放；Caddy 日志 |
| 登录后马上退出 | 确认通过 HTTPS 访问；`HTTPS_ONLY=true` 时 HTTP 不会保存 Secure Cookie |
| 登录返回 403 | CSRF Token 过期；刷新页面后重试 |
| 登录返回 429 | 同一 IP + 用户名 15 分钟内超过 5 次；等待或换账号 |
| 判题返回「缺少 docker 命令」 | 应用镜像没有 Docker CLI；`docker compose build app` 后重启 |
| 判题返回「镜像不可用」 | 先执行 `docker images plg-judge`；没有则 `docker compose build judge-image` |
| 判题容器一直残留 | 检查 `JUDGE_CONCURRENCY`、Docker 守护进程；`docker ps -a | grep plg-judge` |
| 数据库 locked | 确认只有一个 `app` 容器；不要多副本；WAL 与 `busy_timeout` 已开启 |
| 页面没有样式 | `Ctrl+F5`；确认 `style.css?v=9` 返回 200 |
| 判题太慢 | 容器冷启动约 0.5–1 秒；30 人以内建议 `JUDGE_CONCURRENCY=2` |

---

## 7. 安全配置清单

上线前逐项确认：

- [ ] `APP_ENV=production`；
- [ ] `APP_SECRET_KEY` 固定且至少 32 字节随机；
- [ ] `HTTPS_ONLY=true`；
- [ ] `TRUST_PROXY=true`；
- [ ] `JUDGE_MODE=docker`（或明确选择 `disabled`）；
- [ ] `JUDGE_CONCURRENCY` 不超过 4；
- [ ] 只开放 80/443，不暴露 8000；
- [ ] `data/` 持久卷已备份；
- [ ] 已接受 Docker socket 的安全风险；
- [ ] 已阅读 `README.md` 的安全边界。

---

## 8. 本地验证 Docker 判题

如果本机安装了 Docker，可以直接验证判题镜像与单条命令：

```bash
docker build -f deploy/judge.Dockerfile -t plg-judge:latest .
docker run --rm --network none --memory 128m --cpus 0.5 --pids-limit 64 \
  --read-only --tmpfs /work:rw,exec,nosuid,size=16m,mode=1777 \
  -v "$PWD/tmp-judge:/src:ro" -w /work --user 65534:65534 \
  --cap-drop ALL --security-opt no-new-privileges --pull=never \
  plg-judge:latest sh -c "cp /src/main.py /work/main.py && timeout 3 python -I -B -X utf8 /work/main.py"
```

> 本文档对应 M10 产物。当前开发机未安装 Docker，容器实际启动与 HTTPS 证书验证需要在部署服务器上完成。
