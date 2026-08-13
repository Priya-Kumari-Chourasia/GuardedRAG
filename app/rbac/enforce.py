from __future__ import annotations

import logging
from typing import Any, Sequence

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