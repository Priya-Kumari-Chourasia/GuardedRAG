from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import get_settings

# A "turn" = one user question + the assistant's answer to it. Keeping only
# the last few turns bounds prompt size and keeps this a cheap SQLite lookup,
# not a growing-forever context.
MAX_TURNS = 3


def _get_db() -> sqlite3.Connection:
    settings = get_settings()
    Path(settings.ledger_db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.ledger_db_path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY, user_email TEXT NOT NULL, created_at TIMESTAMP NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id TEXT NOT NULL,
            role TEXT NOT NULL, content TEXT NOT NULL, ts TIMESTAMP NOT NULL
        )
        """
    )
    return conn


def start_conversation(user_email: str) -> str:
    conversation_id = str(uuid.uuid4())
    conn = _get_db()
    try:
        conn.execute(
            "INSERT INTO conversations (id, user_email, created_at) VALUES (?, ?, ?)",
            (conversation_id, user_email, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()
    return conversation_id


def append_message(conversation_id: str, role: str, content: str) -> None:
    conn = _get_db()
    try:
        conn.execute(
            "INSERT INTO messages (conversation_id, role, content, ts) VALUES (?, ?, ?, ?)",
            (conversation_id, role, content, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


def get_recent_turns(conversation_id: str, max_turns: int = MAX_TURNS) -> list[dict]:
    """Last `max_turns` user/assistant message pairs, oldest first, ready to
    prepend to a Groq `messages` list.

    This is the ONLY thing carried across turns: past question text and past
    *already-generated* answer text. It deliberately never includes retrieved
    chunk_text. If it did, a later turn could answer from documents that were
    authorized for a PRIOR retrieval call but never re-checked against this
    turn's caller -- e.g. if roles changed mid-conversation, or a doc's ACL
    was tightened via reindex_acl.py between turns. app/api/main.py calls
    retriever.retrieve() fresh on every single turn with the current caller's
    roles; this history is for conversational coherence only ("what about
    last quarter?"), never a substitute for re-running the ACL filter [I1].
    """
    conn = _get_db()
    try:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id DESC LIMIT ?",
            (conversation_id, max_turns * 2),
        ).fetchall()
    finally:
        conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


def get_conversation(conversation_id: str) -> list[dict]:
    """Full transcript for GET /api/conversations/{id} -- unlike get_recent_turns,
    this is not capped to MAX_TURNS; it's the whole stored history."""
    conn = _get_db()
    try:
        rows = conn.execute(
            "SELECT role, content, ts FROM messages WHERE conversation_id = ? ORDER BY id ASC",
            (conversation_id,),
        ).fetchall()
    finally:
        conn.close()
    return [{"role": r["role"], "content": r["content"], "ts": r["ts"]} for r in rows]


def conversation_owner(conversation_id: str) -> str | None:
    conn = _get_db()
    try:
        row = conn.execute(
            "SELECT user_email FROM conversations WHERE id = ?", (conversation_id,)
        ).fetchone()
    finally:
        conn.close()
    return row["user_email"] if row else None
