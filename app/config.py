import os
from pathlib import Path


def _load_dotenv() -> None:
    p = Path(__file__).resolve().parent.parent / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()


class Settings:
    deepseek_api_key: str = os.environ.get("DEEPSEEK_API_KEY", "")
    deepseek_base_url: str = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    deepseek_model: str = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

    app_host: str = os.environ.get("APP_HOST", "0.0.0.0")
    app_port: int = int(os.environ.get("APP_PORT", "8000"))
    db_path: str = os.environ.get("DB_PATH", "data/tutor.db")

    judge_timeout: int = int(os.environ.get("JUDGE_TIMEOUT", "5"))


def get_settings() -> Settings:
    return Settings()