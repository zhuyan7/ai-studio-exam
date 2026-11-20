from app.llm import chat, LLMError
from app.prompts import QA_SYS, QA_USER


def ask(body: dict):
    question = (body.get("question") or "").strip()
    if not question:
        return 400, {"detail": "问题不能为空"}
    try:
        answer = chat(
            QA_USER.format(question=question),
            system_msg=QA_SYS,
            temperature=0.4,
        )
    except LLMError as e:
        return 502, {"detail": str(e)}
    return 200, {"answer": answer}