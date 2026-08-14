"""G4 (budget) -- PLAN.md Phase 4 exit gate ("each of the 7 guardrails has a
unit test"), even though G4 isn't fully wired to real usage numbers until
Phase 6 builds the request_ledger table (SPEC §5.4). See budget.py's
docstring for why check_budget() is a pure function taking
tokens_used_today as a parameter rather than querying anything itself."""

from app.guardrails.budget import check_budget


def test_under_budget_is_not_blocked():
    result = check_budget(tokens_used_today=1000, daily_budget=50000)
    assert result.blocked is False


def test_at_budget_is_blocked():
    result = check_budget(tokens_used_today=50000, daily_budget=50000)
    assert result.blocked is True


def test_over_budget_is_blocked():
    result = check_budget(tokens_used_today=60000, daily_budget=50000)
    assert result.blocked is True
