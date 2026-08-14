from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BudgetResult:
    tokens_used_today: int
    daily_budget: int
    blocked: bool


def check_budget(tokens_used_today: int, daily_budget: int) -> BudgetResult:
    """G4: pure threshold check, deliberately taking tokens_used_today as a
    parameter instead of querying anything itself. SPEC §5.4's
    `request_ledger` table -- the real source of "tokens used today" -- isn't
    built until Phase 6. Keeping this a pure function means it's fully
    testable now, and Phase 6 only has to wire a real lookup at the call
    site; this module never has to change to grow a database dependency.
    """
    return BudgetResult(
        tokens_used_today=tokens_used_today,
        daily_budget=daily_budget,
        blocked=tokens_used_today >= daily_budget,
    )
