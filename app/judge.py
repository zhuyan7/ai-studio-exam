import json
import subprocess
import sys
import textwrap
from app.config import get_settings


def judge_code(user_code: str, tests: list) -> dict:
    s = get_settings()
    test_json = json.dumps(tests, ensure_ascii=False)
    script = textwrap.dedent(f"""
        import json
        __tests = json.loads({test_json!r})
        __results = []
        for __t in __tests:
            __call = __t.get("call")
            __expected = __t.get("expected")
            try:
                __got = eval(__call, globals())
                __ok = __got == __expected
                __results.append({{"call": __call, "passed": __ok,
                                   "got": repr(__got), "expected": repr(__expected)}})
            except Exception as __e:
                __results.append({{"call": __call, "passed": False, "error": str(__e)}})
        print(json.dumps(__results, ensure_ascii=False, default=str))
    """)
    full = user_code + "\n" + script
    try:
        proc = subprocess.run(
            [sys.executable, "-c", full],
            capture_output=True, text=True, timeout=s.judge_timeout,
        )
    except subprocess.TimeoutExpired:
        return {"passed": False, "detail": None, "error": "运行超时（可能存在死循环）"}
    if proc.returncode != 0:
        return {"passed": False, "detail": None,
                "error": (proc.stderr.strip() or "运行出错")[:500]}
    lines = proc.stdout.strip().splitlines()
    if not lines:
        return {"passed": False, "detail": None, "error": "无输出"}
    try:
        results = json.loads(lines[-1])
    except Exception as e:
        return {"passed": False, "detail": proc.stdout[:500], "error": f"解析结果失败: {e}"}
    all_pass = bool(results) and all(r.get("passed") for r in results)
    return {"passed": all_pass, "detail": results, "error": None}