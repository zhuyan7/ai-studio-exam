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
        os.environ[k.strip()] = v.strip()


class Settings:
    def __init__(self):
        _load_dotenv()
        self.deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self.deepseek_base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.deepseek_model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

        self.app_host = os.environ.get("APP_HOST", "0.0.0.0")
        self.app_port = int(os.environ.get("APP_PORT", "8000"))
        self.db_path = os.environ.get("DB_PATH", "data/tutor.db")

        self.judge_timeout = int(os.environ.get("JUDGE_TIMEOUT", "5"))


def get_settings() -> Settings:
    return Settings()