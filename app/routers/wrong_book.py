import json
from datetime import datetime, timezone
from app.db import get_conn
from app.llm import chat, LLMError
from app.prompts import CLASSIFY_SYS, CLASSIFY_USER


def add_wrong(body: dict):
    stem = (body.get("stem") or "").strip()
    if not stem:
        return 400, {"detail": "题目内容不能为空"}
    user_answer = body.get("user_answer")
    error_reason = body.get("error_reason")
    qid = body.get("qid")
    kp_id = body.get("kp_id")
    qtype = body.get("qtype")
    kp_name = None

    if not kp_id or not qtype:
        try:
            raw = chat(
                CLASSIFY_USER.format(
                    stem=stem,
                    user_answer=user_answer or "(未作答)",
                    error_reason=error_reason or "(未说明)",
                ),
                system_msg=CLASSIFY_SYS,
                temperature=0.0,
                json_mode=True,
            )
            obj = json.loads(raw)
            kp_id = obj.get("kp_id", kp_id)
            kp_name = obj.get("kp_name")
            qtype = obj.get("qtype", qtype)
        except (LLMError, json.JSONDecodeError) as e:
            kp_name = f"(归类失败: {e})"

    now = datetime.now(timezone.utc).isoformat()
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO wrong_questions(qid,stem,user_answer,error_reason,kp_id,qtype,created_at) "
            "VALUES(?,?,?,?,?,?,?)",
            (qid, stem, user_answer, error_reason, kp_id, qtype, now),
        )
        wid = cur.lastrowid
        if kp_id:
            conn.execute(
                "INSERT INTO mastery(kp_id,total,wrong,mastery_score) VALUES(?,1,1,0.0) "
                "ON CONFLICT(kp_id) DO UPDATE SET total=total+1, wrong=wrong+1",
                (kp_id,),
            )
        conn.commit()
        row = conn.execute("SELECT * FROM wrong_questions WHERE id=?", (wid,)).fetchone()
    finally:
        conn.close()

    if kp_id and not kp_name:
        r = get_conn().execute(
            "SELECT name FROM knowledge_points WHERE id=?", (kp_id,)).fetchone()
        kp_name = r["name"] if r else None

    return 200, {
        "id": row["id"], "qid": row["qid"], "stem": row["stem"],
        "user_answer": row["user_answer"], "error_reason": row["error_reason"],
        "kp_id": row["kp_id"], "kp_name": kp_name,
        "qtype": row["qtype"], "created_at": row["created_at"],
    }


def list_wrong(limit: int = 100):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT w.*, k.name AS kp_name FROM wrong_questions w "
            "LEFT JOIN knowledge_points k ON w.kp_id=k.id "
            "ORDER BY w.id DESC LIMIT ?", (limit,),
        ).fetchall()
    finally:
        conn.close()
    return 200, [{
        "id": r["id"], "qid": r["qid"], "stem": r["stem"],
        "user_answer": r["user_answer"], "error_reason": r["error_reason"],
        "kp_id": r["kp_id"], "kp_name": r["kp_name"],
        "qtype": r["qtype"], "created_at": r["created_at"],
    } for r in rows]