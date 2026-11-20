from app.db import get_conn


def get_mastery():
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT m.kp_id, k.name, m.total, m.correct, m.wrong, m.mastery_score "
            "FROM mastery m JOIN knowledge_points k ON m.kp_id=k.id "
            "ORDER BY m.mastery_score ASC, m.wrong DESC"
        ).fetchall()
    finally:
        conn.close()
    return 200, [{
        "kp_id": r["kp_id"], "kp_name": r["name"], "total": r["total"],
        "correct": r["correct"], "wrong": r["wrong"], "mastery_score": r["mastery_score"],
    } for r in rows]


def get_weak(top_n: int = 5):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT m.kp_id, k.name, m.total, m.correct, m.wrong, m.mastery_score "
            "FROM mastery m JOIN knowledge_points k ON m.kp_id=k.id "
            "WHERE m.total>0 ORDER BY m.mastery_score ASC, m.wrong DESC LIMIT ?",
            (top_n,),
        ).fetchall()
    finally:
        conn.close()
    return 200, [{
        "kp_id": r["kp_id"], "kp_name": r["name"], "total": r["total"],
        "correct": r["correct"], "wrong": r["wrong"], "mastery_score": r["mastery_score"],
    } for r in rows]


def get_summary():
    conn = get_conn()
    try:
        m = conn.execute(
            "SELECT COUNT(*) AS n, COALESCE(SUM(total),0) AS total, "
            "COALESCE(SUM(correct),0) AS correct, COALESCE(SUM(wrong),0) AS wrong "
            "FROM mastery"
        ).fetchone()
        w = conn.execute("SELECT COUNT(*) AS n FROM wrong_questions").fetchone()
        p = conn.execute("SELECT COUNT(*) AS n FROM practice_records").fetchone()
    finally:
        conn.close()
    return 200, {
        "knowledge_covered": m["n"],
        "total_attempts": m["total"],
        "total_correct": m["correct"],
        "total_wrong": m["wrong"],
        "wrong_questions": w["n"],
        "practice_records": p["n"],
        "accuracy": round(m["correct"] / m["total"], 4) if m["total"] else 0.0,
    }