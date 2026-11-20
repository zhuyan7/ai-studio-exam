import sqlite3
from pathlib import Path
from app.config import get_settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS knowledge_points (
    id   TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    parent TEXT,
    desc TEXT
);

CREATE TABLE IF NOT EXISTS questions (
    id       TEXT PRIMARY KEY,
    stem     TEXT NOT NULL,
    qtype    TEXT NOT NULL,
    kp_id    TEXT NOT NULL,
    solution TEXT,
    tests    TEXT,
    source   TEXT DEFAULT 'seed'
);

CREATE TABLE IF NOT EXISTS wrong_questions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    qid          TEXT,
    stem         TEXT NOT NULL,
    user_answer  TEXT,
    error_reason TEXT,
    kp_id        TEXT,
    qtype        TEXT,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS practice_records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    qid         TEXT,
    stem        TEXT NOT NULL,
    user_answer TEXT,
    passed      INTEGER NOT NULL,
    kp_id       TEXT,
    duration    REAL DEFAULT 0,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mastery (
    kp_id        TEXT PRIMARY KEY,
    total        INTEGER DEFAULT 0,
    correct      INTEGER DEFAULT 0,
    wrong        INTEGER DEFAULT 0,
    mastery_score REAL DEFAULT 0.0
);
"""


def get_conn() -> sqlite3.Connection:
    s = get_settings()
    db_path = Path(s.db_path)
    if not db_path.is_absolute():
        db_path = Path(__file__).resolve().parent.parent / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        conn = sqlite3.connect(str(db_path))
    except sqlite3.OperationalError:
        import tempfile
        db_path = Path(tempfile.gettempdir()) / "python-tutor-ai.db"
        conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_conn()
    try:
        conn.executescript(SCHEMA)
        _seed_knowledge(conn)
        _seed_questions(conn)
        conn.commit()
    finally:
        conn.close()


def _seed_knowledge(conn: sqlite3.Connection) -> None:
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / "data" / "knowledge_tree.json"
    if not p.exists():
        return
    data = json.loads(p.read_text(encoding="utf-8"))
    for pt in data.get("points", []):
        conn.execute(
            "INSERT OR IGNORE INTO knowledge_points(id,name,parent,desc) VALUES(?,?,?,?)",
            (pt["id"], pt["name"], pt.get("parent"), pt.get("desc")),
        )


def _seed_questions(conn: sqlite3.Connection) -> None:
    import json
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / "data" / "seed_questions.json"
    if not p.exists():
        return
    data = json.loads(p.read_text(encoding="utf-8"))
    for q in data:
        conn.execute(
            "INSERT OR IGNORE INTO questions(id,stem,qtype,kp_id,solution,tests,source) "
            "VALUES(?,?,?,?,?,?,?)",
            (q["id"], q["stem"], q["qtype"], q["kp_id"],
             q.get("solution"), json.dumps(q.get("tests", []), ensure_ascii=False), "seed"),
        )