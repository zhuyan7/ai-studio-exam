from fastapi import APIRouter, HTTPException
from app.llm import chat, LLMError
from app.prompts import QA_SYS, QA_USER
from app.models import QAIn

router = APIRouter(prefix="/api/qa", tags=["知识点问答"])


@router.post("", summary="知识点问答（限定 Python 学科）")
async def ask(data: QAIn):
    try:
        answer = await chat(
            QA_USER.format(question=data.question),
            system_msg=QA_SYS,
            temperature=0.4,
        )
    except LLMError as e:
        raise HTTPException(502, str(e))
    return {"answer": answer}