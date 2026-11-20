import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.judge import judge_code


def test_correct_code_passes():
    code = "def add(a, b):\n    return a + b"
    tests = [
        {"call": "add(1, 2)", "expected": 3},
        {"call": "add(-1, 1)", "expected": 0},
    ]
    r = judge_code(code, tests)
    assert r.passed is True
    assert all(d["passed"] for d in r.detail)


def test_wrong_code_fails():
    code = "def add(a, b):\n    return a - b"
    tests = [{"call": "add(1, 2)", "expected": 3}]
    r = judge_code(code, tests)
    assert r.passed is False


def test_syntax_error_captured():
    code = "def add(a, b\n    return a + b"
    tests = [{"call": "add(1, 2)", "expected": 3}]
    r = judge_code(code, tests)
    assert r.passed is False
    assert r.error


def test_runtime_exception_captured():
    code = "def f():\n    return 1 / 0"
    tests = [{"call": "f()", "expected": 1}]
    r = judge_code(code, tests)
    assert r.passed is False
    assert any("error" in d for d in r.detail)


def test_list_return_compared():
    code = "def rev(lst):\n    return lst[::-1]"
    tests = [{"call": "rev([1,2,3])", "expected": [3, 2, 1]}]
    r = judge_code(code, tests)
    assert r.passed is True


def test_empty_tests_not_pass():
    code = "x = 1"
    r = judge_code(code, [])
    assert r.passed is False


if __name__ == "__main__":
    for fn in [test_correct_code_passes, test_wrong_code_fails,
               test_syntax_error_captured, test_runtime_exception_captured,
               test_list_return_compared, test_empty_tests_not_pass]:
        fn()
        print(f"PASS {fn.__name__}")
    print("全部通过")