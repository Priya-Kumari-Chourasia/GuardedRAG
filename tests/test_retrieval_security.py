"""Retrieval-only security eval (PLAN.md task 2.5). No LLM involved -- this
isolates the security border (build_acl_filter + assert_acl) so a failure here
can only mean the border itself is broken, not a generation-layer mistake.

Same 10 topically-diverse queries run under each of the 6 roles = 60 cases.
Every case asserts that every returned chunk's allowed_roles actually includes
the querying role -- i.e. leak_rate 0 for this suite."""

import asyncio

import pytest

from app.rag.retriever import retrieve
from app.rbac.acl import Role

QUERIES = [
    "What was our Q3 2025 net revenue?",
    "Show me employee salary and payroll information",
    "What deals are in the sales pipeline this quarter?",
    "What is our AWS cloud spend?",
    "What is the marketing spend for Q3?",
    "Tell me about the upcoming board deck contents",
    "What are the results of the latest security penetration test?",
    "What is discussed in employee performance reviews?",
    "What restructuring plans are being considered?",
    "What is the company holiday calendar for 2026?",
]

ROLES = [r.value for r in Role]

CASES = [(role, query) for role in ROLES for query in QUERIES]


@pytest.mark.parametrize("role,query", CASES, ids=[f"{r}::{q[:30]}" for r, q in CASES])
def test_no_unauthorized_chunks(role: str, query: str):
    hits = asyncio.run(
        retrieve(query, user_roles=[role], request_id=f"eval-{role}", user_email=f"{role}@pkc.com", top_k=10)
    )
    for hit in hits:
        allowed = hit.payload["allowed_roles"]
        assert role in allowed, (
            f"LEAK: role={role} query={query!r} got chunk={hit.chunk_id} "
            f"whose allowed_roles={allowed} does not include {role}"
        )
