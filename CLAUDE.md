# CLAUDE.md — standing rules for this repo

Claude Code loads this file automatically. It is the short list of things that are always
true here. `SPEC.md` is the full contract; `PLAN.md` is the execution order.

---

## What this project is

An internal RAG assistant where **retrieval is authorization-aware**. The chatbot is the
wrapper; the substance is enforcing per-role document access inside the vector database and
proving in CI that it doesn't leak. Fictional company: **PKC Technologies**. Corpus is 100%
synthetic — never introduce real data.

## Read before writing code

1. `SPEC.md` §1 (hard invariants) — always
2. `SPEC.md` §3.1 (the access matrix) — before touching anything ACL-related
3. `PLAN.md` — find the current task; work only that task

---

## The ten invariants (short form — full text in SPEC §1)

1. ACL enforced via Qdrant `query_filter`. Never post-filter. Never via prompt.
2. Every chunk carries `allowed_roles`; `KEYWORD` payload index required.
3. Post-retrieval `assert_acl` on every result set; P0 on violation.
4. One refusal string for both "not found" and "not authorized" — byte-identical.
5. Guardrails fail closed.
6. Unknown `doc_class` → `(["c_level"], "restricted")`.
7. `build_acl_filter([])` raises.
8. No secrets in source, logs, traces, or commits.
9. All role lists derive from `DOC_CLASS_ACL`. Never inline one.
10. `leak_rate == 0` is a hard gate. Not 0.02.

---

## Working rules

**One task at a time, in `PLAN.md` order.** Do not start the next task until the current
task's **Verify** step passes.

**Run the Verify command and paste the real output.** Never claim a step passed without
executing it. If output contradicts an expectation, say so and stop.

**Commit per task:** `phase<N>: <task> — <what changed>`. Tag per phase.

**Windows / PowerShell.** Project root `E:\secure_knowledge`, venv at `.\venv`. Emit
PowerShell syntax in shell commands (`$env:VAR="x"`, `Select-String`, `.\venv\Scripts\Activate.ps1`),
forward slashes inside Python.

**Python 3.13.** `docling` and `presidio-analyzer` may lack wheels. If install fails, apply
the SPEC §11.1 fallback and **report the substitution explicitly**. Never mark a guardrail
complete if it was silently skipped.

**Free tier only.** Groq ≈30 RPM is the binding constraint. Any batch operation (corpus
generation, ingestion, evals) runs at concurrency ≤ 2 with exponential backoff. Nothing in
this project may require a credit card.

**The user is learning.** When you write a non-obvious file, add a short comment block
explaining *why* the approach was chosen — especially for `async`, retry/backoff,
concurrency, and anything ACL-related. Prefer clarity over cleverness.

---

## Traps that have specific known failure modes

**Hybrid retrieval:** the ACL filter must go on **both** the dense and the sparse (BM25)
arm. Filtering only the dense arm is a leak and is easy to miss.

**Payload index:** forgetting the `KEYWORD` index on `allowed_roles` doesn't error — it
silently degrades every query to a full collection scan.

**Overlap roles:** `cloud_costs` → finance + engineering. `marketing_spend` → finance +
sales. Roles are **not** hierarchical. Any code or eval assuming a clean 1–5 level hierarchy
is wrong.

**Refusal leakage:** "That's restricted to the finance team" is an information leak. Use the
shared template; the message must not vary by role or by reason.

**Eval suites that only test refusals:** a system that refuses everything scores leak_rate 0
and is useless. Security suite must include overlap *positives*.

**Multi-turn memory:** re-run the ACL filter on every turn. Never carry retrieved context
forward without re-authorizing.

---

## Layout

```
app/core/         config, Groq client (retry + backoff + concurrency cap)
app/rbac/         acl.py = the security border · enforce.py = assertion + refusal template
app/rag/          ingest.py · retriever.py · generate.py
app/guardrails/   pipeline.py (G1–G7, ordered, fail-closed)
app/observability/ ledger.py (request ledger + shadow cost)
app/api/          main.py · auth.py
scripts/          generate_corpus · setup_collection · ingest · audit_acl · reindex_acl
evals/            run_evals.py + results/
data/golden/      quality.yaml · security.yaml · adversarial.yaml
tests/            test_acl_matrix.py · test_acl_antipatterns.py (required)
ui/               app.py (Streamlit, light theme, left sidebar)
```

## Already built — verify, don't rewrite

`requirements.txt`, `.gitignore`, `.env`, folder skeleton with `__init__.py`,
`app/core/config.py`, `app/core/groq_client.py`, `scripts/test_groq.py`.

---

## Definition of "done" for any task

The Verify command in `PLAN.md` ran, its real output was shown, and it matched the expected
result. Anything less is in progress.
