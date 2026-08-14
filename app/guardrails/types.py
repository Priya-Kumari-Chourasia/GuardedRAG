from __future__ import annotations

from enum import Enum


class Verdict(str, Enum):
    """SPEC §4.4 verdict enum, written to every ledger row. Str subclass so it
    serializes into the API response / SQLite column as its plain value
    (e.g. "blocked_injection"), not an Enum repr."""

    ALLOWED = "allowed"
    BLOCKED_INJECTION = "blocked_injection"
    BLOCKED_PII = "blocked_pii"
    BLOCKED_OUT_OF_SCOPE = "blocked_out_of_scope"
    BLOCKED_UNGROUNDED = "blocked_ungrounded"
    BLOCKED_BUDGET = "blocked_budget"


# I4 governs ONLY the "document doesn't exist" vs "document exists but you're
# not authorized" pair -- both MUST collapse to enforce.REFUSAL_TEMPLATE.
# Out-of-scope and budget refusals are a different category (nothing to do
# with document existence, nothing to leak by being distinguishable) so they
# get their own, more useful, messages.
OUT_OF_SCOPE_REFUSAL = (
    "That's outside what I can help with. I'm PKC's internal knowledge assistant "
    "and can only answer questions about PKC Technologies."
)

BUDGET_EXCEEDED_REFUSAL = (
    "You've reached your daily usage limit. Please try again tomorrow, or contact "
    "#it-helpdesk if you need it raised."
)
