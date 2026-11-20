import json
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.db import get_conn
from app.llm import chat, LLMError
from app.judge import judge_code
from app.prompts import GEN_PRACTICE_SYS, GEN_PRACTICE_USER
from app.models import PracticeOut, GeneratePracticeIn, JudgeResult

router = APIRouter(prefix="/api/practice", tags=["练习"])


@router.get("/seed", response_model=list[PracticeOut], summary="从题库取题")
def get_seed(kp_id: str = None, limit: int = 10):
    conn = get_conn()
    try:
        if kp_id:
            rows = conn.execute(
                "SELECT q.*, k.name AS kp_name FROM questions q "
                "LEFT JOIN knowledge_points k ON q.kp_id=k.id "
                "WHERE q.kp_id=? ORDER BY RANDOM() LIMIT ?", (kp_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT q.*, k.name AS kp_name FROM questions q "
                "LEFT JOIN knowledge_points k ON q.kp_id=k.id "
                "ORDER BY RANDOM() LIMIT ?", (limit,),
            ).fetchall()
    finally:
        conn.close()
    return [_row_to_out(r) for r in rows]


@router.post("/generate", response_model=list[PracticeOut], summary="按薄弱点生成练习")
async def generate_practice(req: GeneratePracticeIn):
    conn = get_conn()
    try:
        weak = conn.execute(
            "SELECT m.kp_id, k.name, m.wrong FROM mastery m "
            "JOIN knowledge_points k ON m.kp_id=k.id "
            "WHERE m.wrong>0 ORDER BY m.mastery_score ASC, m.wrong DESC LIMIT ?",
            (req.top_n,),
        ).fetchall()
    finally:
        conn.close()

    if not weak:
        raise HTTPException(404, "暂无错题记录，无法定位薄弱点，请先录入错题或练习。")

    out: list[PracticeOut] = []
    for w in weak:
        conn = get_conn()
        try:
            ex = conn.execute(
                "SELECT stem FROM wrong_questions WHERE kp_id=? LIMIT 2", (w["kp_id"],)
            ).fetchall()
        finally:
            conn.close()
        examples = "\n".join(f"- {e['stem']}" for e in ex) or "(无)"
        try:
            raw = await chat(
                GEN_PRACTICE_USER.format(kp_name=w["name"], kp_id=w["kp_id"], examples=examples),
                system_msg=GEN_PRACTICE_SYS,
                temperature=0.7,
                json_mode=True,
            )
            obj = json.loads(raw)
        except (LLMError, json.JSONDecodeError) as e:
            raise HTTPException(502, f"生成练习失败: {e}")

        tests = obj.get("tests", [])
        now = datetime.now(timezone.utc).isoformat()
        conn = get_conn()
        try:
            cur = conn.execute(
                "INSERT INTO questions(id,stem,qtype,kp_id,solution,tests,source) "
                "VALUES(?,?,?,?,?,?,?)",
                (f"gen-{now}-{w['kp_id']}", obj["stem"], "coding", w["kp_id"],
                 obj.get("solution"), json.dumps(tests, ensure_ascii=False), "generated"),
            )
            conn.commit()
        finally:
            conn.close()
        out.append(PracticeOut(
            qid=f"gen-{now}-{w['kp_id']}", stem=obj["stem"], qtype="coding",
            kp_id=w["kp_id"], kp_name=w["name"], tests=tests,
            solution=obj.get("solution"),
        ))
    return out


@router.post("/submit", response_model=JudgeResult, summary="提交作答并判对错")
def submit_practice(qid: str, user_answer: str):
    conn = get_conn()
    try:
        q = conn.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone()
    finally:
        conn.close()
    if not q:
        raise HTTPException(404, "题目不存在")

    tests = json.loads(q["tests"]) if q["tests"] else []
    result = judge_code(user_answer, tests)

    now = datetime.now(timezone.utc).isoformat()
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO practice_records(qid,stem,user_answer,passed,kp_id,created_at) "
            "VALUES(?,?,?,?,?,?)",
            (qid, q["stem"], user_answer, int(result.passed), q["kp_id"], now),
        )
        if result.passed:
            conn.execute(
                "INSERT INTO mastery(kp_id,total,correct,mastery_score) VALUES(?,1,1,1.0) "
                "ON CONFLICT(kp_id) DO UPDATE SET total=total+1, correct=correct+1",
                (q["kp_id"],),
            )
        else:
            conn.execute(
                "INSERT INTO mastery(kp_id,total,wrong,mastery_score) VALUES(?,1,1,0.0) "
                "ON CONFLICT(kp_id) DO UPDATE SET total=total+1, wrong=wrong+1",
                (q["kp_id"],),
            )
            conn.execute(
                "INSERT INTO wrong_questions(qid,stem,user_answer,error_reason,kp_id,qtype,created_at) "
                "VALUES(?,?,?,?,?,?,?)",
                (qid, q["stem"], user_answer, "练习作答错误", q["kp_id"], q["qtype"], now),
            )
        conn.execute(
            "UPDATE mastery SET mastery_score = CASE WHEN total>0 THEN correct*1.0/total ELSE 0 END"
        )
        conn.commit()
    finally:
        conn.close()
    return result


def _row_to_out(r) -> PracticeOut:
    return PracticeOut(
        qid=r["id"], stem=r["stem"], qtype=r["qtype"], kp_id=r["kp_id"],
        kp_name=r["kp_name"], tests=json.loads(r["tests"]) if r["tests"] else None,
        solution=r["solution"],
    )