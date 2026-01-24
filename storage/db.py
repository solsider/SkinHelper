import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any, Set

DB_PATH = Path(__file__).resolve().parent.parent / "bot.db"


def _connect() -> sqlite3.Connection:
    # Открываем соединение на каждую операцию — просто и потокобезопасно для telebot
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

        # миграция для старых БД (если таблица уже была без is_pro)
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(profiles)").fetchall()]
        if "is_pro" not in cols:
            conn.execute("ALTER TABLE profiles ADD COLUMN is_pro INTEGER DEFAULT 0")

        conn.commit()


def get_profile(chat_id: int) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT chat_id, skin_type, problems_json, budget, is_pro FROM profiles WHERE chat_id = ?",
            (chat_id,)
        ).fetchone()

    if not row:
        return None

    problems = set()
    if row["problems_json"]:
        try:
            problems = set(json.loads(row["problems_json"]))
        except Exception:
            problems = set()

    return {
        "skin_type": row["skin_type"],
        "problems": problems,
        "budget": row["budget"],
        "is_pro": bool(row["is_pro"] or 0),
    }


def upsert_profile(
    chat_id: int,
    skin_type: Optional[str] = None,
    problems: Optional[Set[str]] = None,
    budget: Optional[str] = None,
    is_pro: Optional[bool] = None,
) -> None:
    problems_json = None
    if problems is not None:
        problems_json = json.dumps(sorted(list(problems)), ensure_ascii=False)

    is_pro_int = None
    if is_pro is not None:
        is_pro_int = 1 if is_pro else 0

    with _connect() as conn:
        conn.execute("""
        INSERT INTO profiles (chat_id, skin_type, problems_json, budget, is_pro)
        VALUES (?, ?, ?, ?, COALESCE(?, 0))
        ON CONFLICT(chat_id) DO UPDATE SET
            skin_type = COALESCE(excluded.skin_type, profiles.skin_type),
            problems_json = COALESCE(excluded.problems_json, profiles.problems_json),
            budget = COALESCE(excluded.budget, profiles.budget),
            is_pro = COALESCE(excluded.is_pro, profiles.is_pro)
        """, (chat_id, skin_type, problems_json, budget, is_pro_int))
        conn.commit()


def clear_profile(chat_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM profiles WHERE chat_id = ?", (chat_id,))
        conn.commit()
