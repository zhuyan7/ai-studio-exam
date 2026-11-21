import json
import os
import urllib.request
import urllib.error
from typing import Optional
from app.config import get_settings


class LLMError(Exception):
    pass


def chat(
    user_msg: str,
    system_msg: str = "你是一名 Python 程序设计辅导老师。",
    temperature: float = 0.3,
    max_tokens: int = 2048,
    json_mode: bool = False,
) -> str:
    s = get_settings()
    if not s.deepseek_api_key or s.deepseek_api_key.startswith("sk-your"):
        raise LLMError("未配置 DEEPSEEK_API_KEY，请复制 .env.example 为 .env 并填入真实 key。")

    payload: dict = {
        "model": s.deepseek_model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    base = s.deepseek_base_url.rstrip("/")
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {s.deepseek_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        raise LLMError(f"DeepSeek 返回 {e.code}: {e.read().decode('utf-8', 'ignore')[:200]}")
    except (urllib.error.URLError, OSError) as e:
        raise LLMError(f"请求 DeepSeek 失败: {e}")
    except (KeyError, json.JSONDecodeError) as e:
        raise LLMError(f"解析 DeepSeek 响应失败: {e}")