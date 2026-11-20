from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.db import init_db
from app.routers import wrong_book, practice, progress, qa

app = FastAPI(
    title="Python 学习辅导 AI 助教",
    description="面向 Python 程序设计的错题归类 / 薄弱点练习 / 进度记录 / 知识点问答",
    version="1.0.0",
)

app.include_router(wrong_book.router)
app.include_router(practice.router)
app.include_router(progress.router)
app.include_router(qa.router)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def _startup():
    init_db()


@app.get("/")
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/health")
def health():
    return {"status": "ok"}