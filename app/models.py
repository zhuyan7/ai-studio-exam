from pydantic import BaseModel, Field
from typing import Optional, Any


class WrongQuestionIn(BaseModel):
    stem: str = Field(..., description="题目内容")
    user_answer: Optional[str] = Field(None, description="用户当时作答")
    error_reason: Optional[str] = Field(None, description="错误原因")
    qid: Optional[str] = None
    qtype: Optional[str] = None


class WrongQuestionOut(BaseModel):
    id: int
    qid: Optional[str]
    stem: str
    user_answer: Optional[str]
    error_reason: Optional[str]
    kp_id: Optional[str]
    kp_name: Optional[str] = None
    qtype: Optional[str]
    created_at: str


class PracticeIn(BaseModel):
    user_answer: str = Field(..., description="用户提交的 Python 代码")
    qid: Optional[str] = None
    stem: Optional[str] = None
    kp_id: Optional[str] = None


class JudgeResult(BaseModel):
    passed: bool
    detail: Any = None
    error: Optional[str] = None


class PracticeOut(BaseModel):
    qid: Optional[str]
    stem: str
    qtype: str
    kp_id: Optional[str]
    kp_name: Optional[str] = None
    tests: Any = None
    solution: Optional[str] = None


class GeneratePracticeIn(BaseModel):
    top_n: int = Field(3, description="取薄弱点前 N 个生成练习")
    count: int = Field(1, description="每个薄弱点生成题数")


class QAIn(BaseModel):
    question: str = Field(..., description="学生提问")


class MasteryOut(BaseModel):
    kp_id: str
    kp_name: str
    total: int
    correct: int
    wrong: int
    mastery_score: float