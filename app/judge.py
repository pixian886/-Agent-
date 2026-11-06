"""练习判定与编程题判题服务。"""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app.config import (
    DOCKER_BIN,
    JUDGE_CONCURRENCY,
    JUDGE_DOCKER_IMAGE,
    JUDGE_MODE,
)
from app.content import Exercise

MAX_STDERR_CHARS = 500
_MOCK_HTTP_LOCK = threading.Lock()
_DOCKER_JUDGE_SEMAPHORE = threading.Semaphore(JUDGE_CONCURRENCY)


@dataclass(slots=True)
class JudgeResult:
    status: str
    message: str
    test_results: list[dict] = field(default_factory=list)


def judge_choice(exercise: Exercise, answer_index: int) -> JudgeResult:
    """单选题：直接比较选项索引。"""
    if exercise.answer_index is None:
        return JudgeResult("runtime_error", "题目配置缺少答案，请联系管理员")
    if answer_index == exercise.answer_index:
        return JudgeResult("accepted", "回答正确")
    return JudgeResult("wrong_answer", "回答错误，再想一想")


def judge_fill(exercise: Exercise, answer: str) -> JudgeResult:
    """填空题：按题目配置决定是否区分大小写。"""
    user_answer = _normalize_answer(answer, exercise.case_sensitive)
    expected_answers = {
        _normalize_answer(expected, exercise.case_sensitive)
        for expected in exercise.answers
    }
    if user_answer in expected_answers:
        return JudgeResult("accepted", "回答正确")
    return JudgeResult("wrong_answer", "回答错误，再检查一下拼写")


def judge_coding(exercise: Exercise, code: str) -> JudgeResult:
    """按 JUDGE_MODE 选择 subprocess 或 Docker 隔离执行。"""
    if JUDGE_MODE == "docker":
        return _judge_coding_docker(exercise, code)
    return _judge_coding_subprocess(exercise, code)


def _judge_coding_subprocess(exercise: Exercise, code: str) -> JudgeResult:
    """编程题：在临时目录中逐个测试用例执行学生代码。"""
    if not exercise.test_cases:
        return JudgeResult("runtime_error", "题目配置缺少测试用例，请联系管理员")

    with tempfile.TemporaryDirectory(prefix="plg_judge_") as temp_dir:
        script_path = Path(temp_dir) / "main.py"
        script_path.write_text(code, encoding="utf-8")

        mock_context = (
            _mock_http_server(exercise.mock_http)
            if exercise.mock_http
            else contextlib.nullcontext()
        )

        test_results: list[dict] = []
        try:
            with mock_context:
                for index, case in enumerate(exercise.test_cases, start=1):
                    result, should_stop = _run_case(
                        exercise=exercise,
                        case=case,
                        index=index,
                        cwd=temp_dir,
                    )
                    test_results.append(result)
                    if should_stop:
                        break
        except RuntimeError as exc:
            return JudgeResult("runtime_error", str(exc))

    return _summarize_results(exercise, test_results)


def _summarize_results(
    exercise: Exercise, test_results: list[dict]
) -> JudgeResult:
    """把逐用例结果汇总成整体判题状态。"""
    statuses = [result["status"] for result in test_results]
    if "timeout" in statuses:
        status = "timeout"
        message = f"程序运行超过 {exercise.timeout_seconds} 秒"
    elif "runtime_error" in statuses:
        status = "runtime_error"
        message = "程序运行出错，请检查报错信息"
    elif "wrong_answer" in statuses:
        status = "wrong_answer"
        message = "有测试用例未通过"
    else:
        status = "accepted"
        message = "全部测试用例通过"

    return JudgeResult(status=status, message=message, test_results=test_results)


def _run_case(exercise: Exercise, case, index: int, cwd: str):
    """执行单个测试用例，返回结果与是否应停止后续用例。"""
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            [sys.executable, "-I", "-X", "utf8", "main.py"],
            cwd=cwd,
            input=case.stdin,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=exercise.timeout_seconds,
            env=_subprocess_env(exercise),
        )
    except subprocess.TimeoutExpired:
        duration_ms = int((time.perf_counter() - started) * 1000)
        return {
            "index": index,
            "status": "timeout",
            "duration_ms": duration_ms,
            "stdin": case.stdin,
            "expected_stdout": case.expected_stdout,
            "actual_stdout": "",
        }, True

    duration_ms = int((time.perf_counter() - started) * 1000)
    if completed.returncode != 0:
        return {
            "index": index,
            "status": "runtime_error",
            "duration_ms": duration_ms,
            "stdin": case.stdin,
            "expected_stdout": case.expected_stdout,
            "actual_stdout": completed.stdout,
            "stderr": completed.stderr.strip()[-MAX_STDERR_CHARS:],
        }, True

    if _normalize_output(completed.stdout) == _normalize_output(case.expected_stdout):
        return {
            "index": index,
            "status": "accepted",
            "duration_ms": duration_ms,
            "stdin": case.stdin,
            "expected_stdout": case.expected_stdout,
            "actual_stdout": completed.stdout,
        }, False

    return {
        "index": index,
        "status": "wrong_answer",
        "duration_ms": duration_ms,
        "stdin": case.stdin,
        "expected_stdout": case.expected_stdout,
        "actual_stdout": completed.stdout,
    }, False


def _subprocess_env(exercise: Exercise) -> dict[str, str]:
    """把 mock 服务的地址通过环境变量传给学员代码。"""
    env = os.environ.copy()
    if exercise.mock_http:
        env["PLG_MOCK_BASE_URL"] = (
            f"http://127.0.0.1:{exercise.mock_http['port']}"
        )
    return env


def _judge_coding_docker(exercise: Exercise, code: str) -> JudgeResult:
    """在一次性 Docker 容器中执行每个测试用例。"""
    if not exercise.test_cases:
        return JudgeResult("runtime_error", "题目配置缺少测试用例，请联系管理员")

    with tempfile.TemporaryDirectory(prefix="plg_judge_") as temp_dir:
        script_path = Path(temp_dir) / "main.py"
        script_path.write_text(code, encoding="utf-8")
        _prepare_docker_files(exercise, temp_dir)

        test_results: list[dict] = []
        for index, case in enumerate(exercise.test_cases, start=1):
            result, should_stop = _run_case_docker(
                exercise=exercise,
                case=case,
                index=index,
                cwd=temp_dir,
            )
            test_results.append(result)
            if should_stop:
                break

    return _summarize_results(exercise, test_results)


def _prepare_docker_files(exercise: Exercise, temp_dir: str) -> None:
    """准备 mock 配置与容器内 runner，并放开只读挂载所需权限。"""
    if exercise.mock_http:
        (Path(temp_dir) / "mock_config.json").write_text(
            json.dumps(exercise.mock_http, ensure_ascii=False),
            encoding="utf-8",
        )
        shutil.copyfile(
            Path(__file__).with_name("sandbox_runner.py"),
            Path(temp_dir) / "sandbox_runner.py",
        )

    try:
        os.chmod(temp_dir, 0o755)
        for path in Path(temp_dir).iterdir():
            os.chmod(path, 0o644)
    except OSError:
        # Windows 上 chmod 语义有限；Docker Desktop 的挂载通常仍可读。
        pass


def _docker_inner_command(exercise: Exercise) -> str:
    """容器内命令：复制代码到可写 tmpfs，再限时执行。"""
    timeout = exercise.timeout_seconds
    if exercise.mock_http:
        return (
            "cp /src/main.py /work/main.py && "
            "cp /src/sandbox_runner.py /work/sandbox_runner.py && "
            "cp /src/mock_config.json /work/mock_config.json && "
            f"timeout {timeout} python -I -B -X utf8 /work/sandbox_runner.py"
        )
    return (
        "cp /src/main.py /work/main.py && "
        f"timeout {timeout} python -I -B -X utf8 /work/main.py"
    )


def _run_case_docker(exercise: Exercise, case, index: int, cwd: str):
    """在隔离容器中执行单个用例，返回结果与是否应停止。"""
    started = time.perf_counter()
    container_name = f"plg-judge-{uuid.uuid4().hex[:12]}"
    command = [
        DOCKER_BIN,
        "run",
        "--rm",
        "-i",
        "--name",
        container_name,
        "--network",
        "none",
        "--memory",
        "128m",
        "--memory-swap",
        "128m",
        "--cpus",
        "0.5",
        "--pids-limit",
        "64",
        "--read-only",
        "--tmpfs",
        "/work:rw,exec,nosuid,size=16m,mode=1777",
        "-v",
        f"{Path(cwd).resolve().as_posix()}:/src:ro",
        "-w",
        "/work",
        "--user",
        "65534:65534",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "-e",
        "TMPDIR=/work",
        "-e",
        "HOME=/work",
        "-e",
        "PYTHONDONTWRITEBYTECODE=1",
        "--pull=never",
        JUDGE_DOCKER_IMAGE,
        "sh",
        "-c",
        _docker_inner_command(exercise),
    ]

    try:
        with _DOCKER_JUDGE_SEMAPHORE:
            completed = subprocess.run(
                command,
                input=case.stdin,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=exercise.timeout_seconds + 5,
            )
    except FileNotFoundError:
        return {
            "index": index,
            "status": "runtime_error",
            "duration_ms": 0,
            "stdin": case.stdin,
            "expected_stdout": case.expected_stdout,
            "actual_stdout": "",
            "stderr": "判题服务器缺少 docker 命令，请检查 DOCKER_BIN",
        }, True
    except subprocess.TimeoutExpired:
        _remove_container(container_name)
        duration_ms = int((time.perf_counter() - started) * 1000)
        return {
            "index": index,
            "status": "timeout",
            "duration_ms": duration_ms,
            "stdin": case.stdin,
            "expected_stdout": case.expected_stdout,
            "actual_stdout": "",
        }, True

    duration_ms = int((time.perf_counter() - started) * 1000)
    if completed.returncode == 124:
        return {
            "index": index,
            "status": "timeout",
            "duration_ms": duration_ms,
            "stdin": case.stdin,
            "expected_stdout": case.expected_stdout,
            "actual_stdout": completed.stdout,
        }, True

    if completed.returncode != 0:
        stderr = completed.stderr.strip()[-MAX_STDERR_CHARS:]
        if completed.returncode == 125:
            stderr = f"判题镜像不可用（{JUDGE_DOCKER_IMAGE}）：{stderr}"
        return {
            "index": index,
            "status": "runtime_error",
            "duration_ms": duration_ms,
            "stdin": case.stdin,
            "expected_stdout": case.expected_stdout,
            "actual_stdout": completed.stdout,
            "stderr": stderr or f"docker 退出码 {completed.returncode}",
        }, True

    if _normalize_output(completed.stdout) == _normalize_output(
        case.expected_stdout
    ):
        return {
            "index": index,
            "status": "accepted",
            "duration_ms": duration_ms,
            "stdin": case.stdin,
            "expected_stdout": case.expected_stdout,
            "actual_stdout": completed.stdout,
        }, False

    return {
        "index": index,
        "status": "wrong_answer",
        "duration_ms": duration_ms,
        "stdin": case.stdin,
        "expected_stdout": case.expected_stdout,
        "actual_stdout": completed.stdout,
    }, False


def _remove_container(container_name: str) -> None:
    """超时后强制清理可能残留的判题容器。"""
    try:
        subprocess.run(
            [DOCKER_BIN, "rm", "-f", container_name],
            capture_output=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass


@contextlib.contextmanager
def _mock_http_server(config: dict):
    """在 127.0.0.1 上启动一个只读 mock 服务，供 HTTP 类站内题使用。"""
    if not _MOCK_HTTP_LOCK.acquire(timeout=10):
        raise RuntimeError("判题服务繁忙，请稍后重试")

    server: ThreadingHTTPServer | None = None
    thread: threading.Thread | None = None
    try:
        handler = _build_mock_handler(config)
        try:
            server = _ReusableHTTPServer(("127.0.0.1", config["port"]), handler)
        except OSError as exc:
            raise RuntimeError(
                f"mock 端口 {config['port']} 被占用，请稍后重试"
            ) from exc

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        yield config
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None:
            thread.join(timeout=2)
        _MOCK_HTTP_LOCK.release()


class _ReusableHTTPServer(ThreadingHTTPServer):
    """允许快速重启，避免连续判题时端口处于 TIME_WAIT。"""

    allow_reuse_address = True
    daemon_threads = True


def _build_mock_handler(config: dict):
    """按配置返回固定 JSON；未知城市返回 default 或 404。"""
    path = config["path"]
    query_key = config["query_key"]
    responses = config["responses"]
    default = config.get("default")

    class MockHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path != path:
                self.send_error(404, "Not Found")
                return

            value = parse_qs(parsed.query).get(query_key, [""])[0]
            payload = responses.get(value, default)
            if payload is None:
                self.send_error(404, "Unknown value")
                return

            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            return

    return MockHandler


def _normalize_output(text: str) -> str:
    """统一换行符，去掉每行行尾空格与整个输出的末尾空白。"""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in normalized.split("\n")]
    return "\n".join(lines).rstrip()


def _normalize_answer(text: str, case_sensitive: bool) -> str:
    """填空题答案归一化：去首尾空格，按需忽略大小写。"""
    normalized = text.strip()
    return normalized if case_sensitive else normalized.casefold()
