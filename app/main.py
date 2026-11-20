import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path

from app.config import get_settings
from app.db import init_db
from app.judge import judge_code
from app.routers import wrong_book, practice, progress, qa

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send_json(self, code, data):
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, code, text, ctype="text/plain; charset=utf-8"):
        body = text.encode("utf-8") if isinstance(text, str) else text
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        u = urlparse(self.path)
        path, query = u.path, parse_qs(u.query)

        if path == "/" or path == "/index.html":
            self._serve_static("index.html")
            return
        if path.startswith("/static/"):
            self._serve_static(path[len("/static/"):])
            return
        if path == "/api/health":
            self._send_json(200, {"status": "ok"})
            return

        try:
            if path == "/api/wrong":
                code, data = wrong_book.list_wrong(int(query.get("limit", ["100"])[0]))
            elif path == "/api/practice/seed":
                kp = query.get("kp_id", [None])[0]
                code, data = practice.get_seed(kp, int(query.get("limit", ["10"])[0]))
            elif path == "/api/progress/mastery":
                code, data = progress.get_mastery()
            elif path == "/api/progress/weak":
                code, data = progress.get_weak(int(query.get("top_n", ["5"])[0]))
            elif path == "/api/progress/summary":
                code, data = progress.get_summary()
            else:
                self._send_json(404, {"detail": "未找到"})
                return
            self._send_json(code, data)
        except Exception as e:
            self._send_json(500, {"detail": f"服务器错误: {e}"})

    def do_POST(self):
        u = urlparse(self.path)
        path = u.path
        body = self._read_body()

        try:
            if path == "/api/wrong":
                code, data = wrong_book.add_wrong(body)
            elif path == "/api/practice/generate":
                code, data = practice.generate_practice(body)
            elif path == "/api/practice/submit":
                qid = parse_qs(u.query).get("qid", [None])[0]
                if not qid:
                    self._send_json(400, {"detail": "缺少 qid 参数"})
                    return
                code, data = practice.submit_practice(qid, body)
            elif path == "/api/qa":
                code, data = qa.ask(body)
            else:
                self._send_json(404, {"detail": "未找到"})
                return
            self._send_json(code, data)
        except Exception as e:
            self._send_json(500, {"detail": f"服务器错误: {e}"})

    def _serve_static(self, name: str):
        p = (STATIC_DIR / name).resolve()
        if not p.is_file() or STATIC_DIR not in p.parents:
            self._send_text(404, "未找到")
            return
        ctype = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
        self._send_text(200, p.read_bytes(), ctype)


def create_server() -> ThreadingHTTPServer:
    init_db()
    s = get_settings()
    return ThreadingHTTPServer((s.app_host, s.app_port), Handler)


def main():
    server = create_server()
    s = get_settings()
    print(f"Python 学习辅导 AI 助教已启动：http://localhost:{s.app_port}")
    print(f"API 文档见 README，Swagger 已移除（零依赖版本）")
    print(f"按 Ctrl+C 停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
        server.shutdown()


if __name__ == "__main__":
    main()