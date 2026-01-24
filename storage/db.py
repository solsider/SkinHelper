import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any, Set

DB_PATH = Path(__file__).resolve().parent.parent / "bot.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")

        conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            chat_id INTEGER PRIMARY KEY,
            skin_type TEXT,
            problems_json TEXT,
            budget TEXT,
            is_pro INTEGER DEFAULT 0
        )
        """)

        # миграция: если таблица была создана раньше без is_pro
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(profiles)").fetchall()]
        if "is_pro" not in cols:
            conn.execute("ALTER TABLE profiles ADD COLUMN is_pro INTEGER DEFAULT 0;")

        conn.commit()


def get_profile(chat_id: int) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT chat_id, skin_type, problems_json, budget, is_pro FROM profiles WHERE chat_id = ?",
            (chat_id,)
        ).fetchone()

    if not row:
        return None

    problems: Set[str] = set()
    if row["problems_json"]:
        try:
            problems = set(json.loads(row["problems_json"]))
        except Exception:
            problems = set()

    return {
        "skin_type": row["skin_type"],
        "problems": problems,
        "budget": row["budget"],
        "is_pro": bool(row["is_pro"])  # ✅ важно
    }


def upsert_profile(
    chat_id: int,
    skin_type: Optional[str] = None,
    problems: Optional[Set[str]] = None,
    budget: Optional[str] = None,
    is_pro: Optional[bool] = None
) -> None:
    existing = get_profile(chat_id) or {
        "skin_type": None,
        "problems": set(),
        "budget": None,
        "is_pro": False,
    }

    skin_type = skin_type if skin_type is not None else existing["skin_type"]
    problems = problems if problems is not None else existing["problems"]
    budget = budget if budget is not None else existing["budget"]
    is_pro_val = int(is_pro) if is_pro is not None else int(existing["is_pro"])

    problems_json = json.dumps(sorted(list(problems)), ensure_ascii=False)

    with _connect() as conn:
        conn.execute("""
        INSERT INTO profiles (chat_id, skin_type, problems_json, budget, is_pro)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(chat_id) DO UPDATE SET
            skin_type=excluded.skin_type,
            problems_json=excluded.problems_json,
            budget=excluded.budget,
            is_pro=excluded.is_pro
        """, (chat_id, skin_type, problems_json, budget, is_pro_val))
        conn.commit()


def clear_profile(chat_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM profiles WHERE chat_id = ?", (chat_id,))
        conn.commit()
