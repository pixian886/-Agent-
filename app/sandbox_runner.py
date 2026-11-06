"""在判题容器内启动 mock HTTP 服务并执行学员代码。

这个文件会被复制到临时目录，再挂载进判题容器；它只使用标准库，
不依赖平台代码。
"""

from __future__ import annotations

import json
import runpy
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

CONFIG_PATH = "/work/mock_config.json"
STUDENT_PATH = "/work/main.py"


def main() -> None:
    with open(CONFIG_PATH, encoding="utf-8") as config_file:
        config = json.load(config_file)

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

    server = ThreadingHTTPServer(("127.0.0.1", config["port"]), MockHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        runpy.run_path(STUDENT_PATH, run_name="__main__")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
