import httpx
from typing import Optional
from app.config import get_settings


class LLMError(Exception):
    pass


async def chat(
    user_msg: str,
    system_msg: str = "你是一名 Python 程序设计辅导老师。",
    temperature: float = 0.3,
    max_tokens: int = 2048,
    json_mode: bool = False,
) -> str:
    s = get_settings()
    if not s.deepseek_api_key or s.deepseek_api_key.startswith("sk-your"):
        raise LLMError("未配置 DEEPSEEK_API_KEY，请复制 .env.example 为 .env 并填入真实 key。")

    headers = {
        "Authorization": f"Bearer {s.deepseek_api_key}",
        "Content-Type": "application/json",
    }
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
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(f"{base}/chat/completions", headers=headers, json=payload)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        raise LLMError(f"DeepSeek 返回 {e.response.status_code}: {e.response.text[:200]}")
    except httpx.HTTPError as e:
        raise LLMError(f"请求 DeepSeek 失败: {e}")