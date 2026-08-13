from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ACLViolation(Exception):
    """Raised when a chunk reaches a user who is not authorized for it."""


REFUSAL_TEMPLATE = (
    "I couldn't find information available to you that answers this question. "
    "If you believe you should have access, contact your manager or #it-helpdesk."
)


def assert_acl(
    hits: Sequence[Any],
    user_roles: list[str],
    request_id: str,
    user_email: str,
) -> None:
    allowed = set(user_roles)
    for hit in hits:
        chunk_roles = set(hit.payload.get("allowed_roles", []))
        if not chunk_roles & allowed:
            chunk_id = hit.payload.get("chunk_id", "<unknown>")
            log_security_event(
                severity="P0",
                event_type="acl_assertion_failure",
                user_email=user_email,
                request_id=request_id,
                detail=f"chunk={chunk_id} chunk_roles={sorted(chunk_roles)} user_roles={sorted(allowed)}",
            )
            raise ACLViolation(chunk_id)


def log_security_event(
    *,
    severity: str,
    event_type: str,
    user_email: str,
    detail: str,
    request_id: str | None = None,
) -> None:
    logger.error("SECURITY %s %s user=%s request=%s :: %s", severity, event_type, user_email, request_id, detail)

    # Structured log above is for local dev visibility; this DB write is what the
    # admin dashboard (Phase 6) and eval suite actually query. If the write fails,
    # we still keep the log line above -- a broken DB should not hide a P0 in the
    # console, but it also must not silently swallow the failure.
    settings = get_settings()
    Path(settings.ledger_db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.ledger_db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY, ts TIMESTAMP NOT NULL, severity TEXT NOT NULL,
                event_type TEXT NOT NULL, user_email TEXT NOT NULL, request_id TEXT,
                detail TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "INSERT INTO security_events (ts, severity, event_type, user_email, request_id, detail) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), severity, event_type, user_email, request_id, detail),
        )
        conn.commit()
    finally:
        conn.close()