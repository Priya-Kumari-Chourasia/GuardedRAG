# PLAN.md — Execution plan for Claude Code

> **Companion to `SPEC.md`.** SPEC is the contract; this is the order of operations.
> Work **one task at a time, in order**. Each task has an explicit **Verify** step with a
> runnable command. **Do not start the next task until the current task's Verify passes.**
> Report the actual command output — never assert that a step passed without running it.

**Environment:** Windows / PowerShell / VS Code. Root `E:\secure_knowledge`. Python 3.13
inside `.\venv`. Activate with `.\venv\Scripts\Activate.ps1` before any Python command.

---

## Conventions for every task

- **Commit at the end of each task**, message format: `phase<N>: <task> — <what changed>`.
- Tag at the end of each phase: `git tag v0.<phase>-<slug>`.
- If a Verify fails, **fix it before moving on**. Do not accumulate broken steps.
- If a dependency won't install, apply SPEC §11.1 fallbacks and report the substitution.
- Never write a secret into a tracked file.
- When a task says "MUST", it maps to a SPEC invariant — do not negotiate it away.

---

## Phase 0 — Foundations  *(partially complete)*

**Goal:** everything is wired; nothing does real work yet.

### ✅ 0.1 — Already done, verify only
`requirements.txt`, `.gitignore`, `.env`, folder skeleton with `__init__.py`,
`app/core/config.py`, `app/core/groq_client.py`, `scripts/test_groq.py`.

**Verify:**
```powershell
python -c "from app.core.config import get_settings; s=get_settings(); print('groq configured:', s.groq_configured); print('collection:', s.qdrant_collection)"
python scripts/test_groq.py
```
Expect `groq configured: True`, `collection: pkc_tech`, and a real AI reply with token counts.

### 0.2 — Extend `config.py` to the full settings surface
Add every field referenced anywhere in SPEC that is not yet present: `embed_model`,
`embed_dim`, `top_k`, `use_hybrid`, `rrf_k`, `injection_threshold`,
`out_of_scope_threshold`, `faithfulness_threshold`, `enable_groundedness_check`,
`guardrails_fail_closed`, `jwt_algorithm`, `jwt_expire_minutes`, `langchain_*`,
`ledger_db_path`, `daily_token_budget`, `daily_shadow_cost_alert_usd`,
`groq_guard_model`. Add matching entries to `.env` and create `.env.example` (same keys,
placeholder values, **safe to commit**).

**Verify:** `python -c "from app.core.config import get_settings; print(get_settings().model_dump())"` prints all fields; then confirm bad input fails fast:
```powershell
$env:TOP_K="not-a-number"; python -c "from app.core.config import Settings; Settings()"; Remove-Item Env:TOP_K
```
Expect a Pydantic `ValidationError` — that is the pass condition.

### 0.3 — Qdrant Cloud connectivity check
No local Docker needed — `.env`'s `QDRANT_URL` already points at a live Qdrant Cloud free
cluster, used for both dev and prod. Confirm the app can actually reach it and authenticate.

**Verify:**
```powershell
python -c "from qdrant_client import QdrantClient; from app.core.config import get_settings; s=get_settings(); c=QdrantClient(url=s.qdrant_url, api_key=s.qdrant_api_key); print(c.get_collections())"
```
Expect a `CollectionsResponse` (empty list is fine — the collection doesn't exist yet, that's task 1.3).

### 0.4 — `/health` endpoint in `app/api/main.py`
Per SPEC §4.5. Pings Qdrant, reports whether Groq is configured. **MUST NOT** call the Groq API.

**Verify:**
```powershell
uvicorn app.api.main:app --reload
# separate terminal:
curl http://localhost:8000/health
```
Expect `{"status":"ok","qdrant":{"status":"ok"},"groq":{"status":"ok"},...}`.

**Phase 0 exit gate:** all four verifies pass. Tag `v0.1-foundations`.

---

## Phase 1 — Corpus & ingestion

**Goal:** 100 ACL-tagged documents, chunked, embedded, searchable.

### ✅ 1.1 — `app/rbac/acl.py`
Implement SPEC §4.1 exactly: `Role`, `Sensitivity`, `DOC_CLASS_ACL` (all 30 rows from
§3.1), `acl_for`, `most_restrictive`, `build_acl_filter`.

**Do first, before any corpus code** — ingestion derives its tags from this module [I9].

**Verify:** write and run `tests/test_acl_matrix.py` asserting the structural properties
in SPEC §3.1: 30 entries; `c_level` in every row; no `employee` on confidential/restricted;
`acl_for("cloud_costs")` == finance+engineering+c_level; `acl_for("marketing_spend")` ==
finance+sales+c_level; `acl_for("typo_class")` == `(["c_level"], "restricted")`;
`build_acl_filter([])` raises `ValueError`. All MUST pass.

### ✅ 1.2 — `scripts/generate_corpus.py`
**Actual implementation differs from the original plan below — noted 2026-08-14.** Built as
pure LLM generation via `get_groq_client()`, with a static `scripts/corpus_manifest.py`
(100 entries, doc_class/department/special_case per doc) driving the prompts, and per-case
instructions injected for the 5 deliberate cases. No `--seed` flag and no Faker: PII fields
are LLM-generated from an instruction, not deterministically sampled. Runs are NOT
byte-reproducible. Concurrency capped via `GROQ_MAX_CONCURRENCY` semaphore inside
`groq_client.py`; already-generated files are skipped on re-run, so the script is safe to
re-invoke to fill in gaps.

~~100 docs per SPEC §8 department split, `--seed` for determinism, Faker for synthetic PII~~

**All five deliberate cases from SPEC §8 MUST be present.**

**Verify (actual):** `python -m scripts.generate_corpus` produces 100 files split
15/20/20/18/18/9 across departments (confirmed). All 5 deliberate cases confirmed present
via `scripts/corpus_manifest.py`'s `special_case`/`contains_pii` tags, and the poisoned doc
(`eng-postmortem-embedding-latency`) manually confirmed to contain the literal injection
payload. **Known issue hit and fixed:** first run used `max_tokens=1400`, which truncated
20/100 docs (including the poisoned doc, before the payload). Bumped to `max_tokens=2000`
and regenerated the 20 truncated docs; second pass had zero truncations.

### ✅ 1.3 — `scripts/setup_collection.py`
Create the Qdrant collection (384-dim, cosine) **and** the `KEYWORD` payload index on
`allowed_roles` [I2]. Idempotent — safe to re-run.

**Verify:** `curl http://localhost:6333/collections/pkc_tech` shows the collection and the
`allowed_roles` index in its payload schema.

### ✅ 1.4 — `app/rag/ingest.py`
Parse → structure-aware chunk (512/64/100-min, header injection) → tag via `acl_for()` →
apply `most_restrictive()` for multi-section chunks → embed (FastEmbed, local) → batch upsert.

**Actual chunk count: 356, not ~1,000-1,400** — that estimate assumed longer/PDF-sourced
docs; our 100 LLM-generated docs run 300-650 words each, so most produce 1-2 chunks. Real
number confirmed both from ingest output and `points_count` on the live collection.

**Known issue hit and fixed:** default FastEmbed `batch_size=256` caused an onnxruntime
"bad allocation" / page-file-exhaustion crash on this machine. Tried `parallel=0` as a
fix, which made it *worse* -- FastEmbed treats `0` as "use `os.cpu_count()` worker
subprocesses," not "disable parallelism." Correct fix: `parallel=None` (true sequential,
single-process) + small `batch_size=8`.

**Verify:** `python -m scripts.ingest` reports actual chunk count (356). Then a raw filtered query
returns zero finance chunks for an employee:
```powershell
python -c "from qdrant_client import QdrantClient, models; c=QdrantClient('http://localhost:6333'); r=c.scroll('pkc_tech', scroll_filter=models.Filter(must=[models.FieldCondition(key='allowed_roles', match=models.MatchAny(any=['employee']))]), limit=1000)[0]; print('employee-visible chunks:', len(r)); print('finance leaks:', sum(1 for p in r if p.payload['department']=='finance'))"
```
Expect `finance leaks: 0`.

### ✅ 1.5 — `scripts/audit_acl.py`
Print every chunk with its assigned roles, grouped by department.

**Verify:** run it and read the output fully once. Ten minutes here prevents a confusing
eval failure in Phase 5. Done 2026-08-14 -- read all 356 chunks across 6 departments, both
overlap classes (`cloud_costs`, `marketing_spend`) tagged correctly, zero `employee` access
on any confidential/restricted doc.

**Phase 1 exit gate:** 100 docs → 356 chunks (not ~1.2k, see 1.2/1.4 notes), audit output
correct, `finance leaks: 0`. Tag `v0.2-ingestion`.

---

## Phase 2 — RBAC  ← the differentiator, do not rush this

**Goal:** retrieval is authorization-aware and *provably* so. No LLM generation yet.

### ✅ 2.1 — `app/api/auth.py`
bcrypt password hashing, JWT with role claims, 6 seeded users from SPEC §3,
`get_current_user` FastAPI dependency, `POST /api/auth/login`.
Deliberately simple — real IdP integration is an explicit non-goal.

**Verify:** log in as each of the 6 users; each token decodes to the correct roles.

### ✅ 2.2 — `app/rbac/enforce.py`
`REFUSAL_TEMPLATE` (exact string from SPEC §4.2), `ACLViolation`, `assert_acl`,
`log_security_event` writing to `security_events`.

**Verify:** unit test — a hit whose `allowed_roles` is disjoint from the caller's roles
raises `ACLViolation` and writes one P0 row.

### ✅ 2.3 — `app/rag/retriever.py`
**Scoped to dense-only, by explicit choice 2026-08-14** -- SPEC's hybrid dense+BM25 design
would require reconfiguring the Qdrant collection for sparse vectors and re-ingesting all
356 chunks. `PLAN.md`'s own "cut list" names this as the first thing to cut if short on
time, so no sparse arm exists and there is no second arm to forget to filter. ACL filter
[I1] is passed straight into Qdrant's `query_filter` on the one (dense) query, then
`assert_acl` [I3] runs as defense-in-depth. Document this scoping decision in
`docs/DESIGN_DECISIONS.md` (Phase 6) as a deliberate trade-off, not an oversight.

**Verify (actual):** smoke-tested `retrieve()` with the identical query ("What was our Q3
2025 net revenue?") as `employee` vs `finance_analyst` -- employee got 5 company-wide
chunks, zero finance content; finance_analyst got the actual Q3 report/forecast chunks.
No `ACLViolation` raised. Formal proof that this generalizes across all roles is task 2.5.

~~**Verify:** deliberately remove the filter from the sparse arm only...~~ (N/A -- no sparse arm)

### ✅ 2.4 — `tests/test_acl_antipatterns.py`  **(required deliverable)**
Implement all three broken approaches from SPEC §6 and prove each fails. These tests pass
by demonstrating failure. Include a docstring on each explaining the failure mode in one
sentence — this file is interview material as much as it is a test.

**Verify:** `pytest tests/test_acl_antipatterns.py -v` — 3 passed.

### ✅ 2.5 — Retrieval-only security eval
For each of the 6 roles, 10 queries, assert zero unauthorized chunks. **No LLM involved** —
this isolates the security border so failures are unambiguous.

Implemented as `tests/test_retrieval_security.py`, parametrized pytest: 10 topically-diverse
queries (finance, HR, sales, engineering, exec, company-wide) x 6 roles = 60 cases.

**Verify:** 60 cases, 0 unauthorized chunks, all roles. **Actual: 60 passed, 0 failed.**

**Phase 2 exit gate:** 60 retrieval cases clean; 3 anti-pattern tests pass. Tag `v0.3-rbac`.
Screenshot the passing security test output — it goes in the README.

---

## Phase 3 — Generation

**Goal:** it answers questions, with citations.

### ✅ 3.1 — `app/rag/generate.py`
System prompt from SPEC §9, numbered passages, citation markers `[doc_id::chunk]`,
citation parsing back to structured `citations[]`.

**Known issue hit and fixed:** Groq's model sometimes emits citation markers with
fullwidth brackets (`【doc_id::c01】`) instead of ASCII `[doc_id::c01]`. The parser
regex now accepts both — rejecting the fullwidth form would have turned correctly-cited,
grounded answers into false refusals.

### ✅ 3.2 — Refusal handling
Every refusal path uses `enforce.REFUSAL_TEMPLATE` [I4].

**Verify (actual):** `Select-String -Recurse` isn't valid syntax on Windows PowerShell
5.1 (`Select-String` has no `-Recurse` param there); ran
`Get-ChildItem -Recurse | Select-String` instead. One hit in source
(`app/rbac/enforce.py`); a second hit in `__pycache__/*.pyc` is just the compiled
bytecode cache of that same file, not a real duplicate.

**Non-obvious extension beyond the literal task:** a single call site for the constant
isn't sufficient for I4 by itself — retrieval can return hits that are authorized but
irrelevant, and the LLM will then write its own "the passages don't cover this" sentence
instead of using the constant. `generate.py` now collapses any answer with zero *resolved*
citations (real or hallucinated) to `REFUSAL_TEMPLATE` too, closing that gap.

### ✅ 3.3 — Conversation memory (last 3 turns)
`app/rag/memory.py`. **Re-run the ACL filter on every turn.** Stores only past
question/answer TEXT, never past retrieved `chunk_text` — history is for conversational
continuity only, never a substitute for re-authorizing retrieval on the current turn.

### ✅ 3.4 — `POST /api/chat`
Full contract from SPEC §4.5, plus `GET /api/conversations/{id}` (owner-only; a
non-owner gets the same 404 as a nonexistent ID — no existence leak, same principle as I4).

**Corpus bug found and fixed during exit-gate testing (2026-08-14):**
`data/raw/company_wide/co-org-chart-q3-2025.md` (`doc_class: org_chart`, sensitivity
`internal`, visible to **all roles**) contained named-executives' individual salaries
and a "Key Figures (Q3-2025)" block whose `Net Revenue: ₹42.7 crore` was an **exact
duplicate** of the confidential `fin-q3-2025-report.md` figure (finance_analyst + c_level
only). Not an ACL-enforcement bug — retrieval correctly returned only chunks `employee`
is authorized for; the leak was baked into the corpus during Phase 1 generation.
`special_case` for this doc was `null` — unintentional, not one of the 5 deliberate cases.
Audited the rest of the company-wide corpus (15 docs) for the same pattern via exact
monetary-figure overlap with finance/HR docs; every other overlap spot-checked back to
coincidental reuse of round figures (e.g. `co-it-howto-vpn.md`'s "Rohan Mehta — ₹12.5 L"
is a VPN-licence line-item cost naming him as budget approver, not his salary), not a
genuine duplicate disclosure. Stripped the compensation/financial figures from the org
chart, deleted its stale Qdrant points (chunk count shrank, and upsert-by-deterministic-id
doesn't clean up chunks that no longer exist), re-ran `python -m scripts.ingest`. Full
existing suite (70 tests across `test_acl_matrix`, `test_acl_antipatterns`,
`test_retrieval_security`) still green afterward.

**Phase 3 exit gate (actual):** `arjun@pkc.com` asks about Q3 revenue → grounded answer
citing `fin-q3-2025-report::c01`/`c02`. `ravi@pkc.com` asks the identical question →
`REFUSAL_TEMPLATE`, byte-identical to the not-found refusal. **Verified.** Tagged
`v0.4-generation`.

---

## Phase 4 — Guardrails

**Goal:** hostile input handled; fail closed [I5].

### ✅ 4.1 — G1 injection · 4.2 — G2 input PII · 4.3 — G3 out-of-scope
Per SPEC §4.4. For G3, compute the corpus centroid once at ingest and cache it
(`ingest.py` now writes `data/corpus_centroid.json` -- 384-dim, normalized -- alongside
every upsert).

`presidio-analyzer`/`presidio-anonymizer` **installed cleanly on Python 3.13** -- the SPEC
§11.1 regex fallback was not needed. `AnalyzerEngine()` auto-downloaded its spaCy model
(`en_core_web_lg`, ~400MB) on first use. PKC is an Indian company; Presidio ships no
PAN/Aadhaar recognizers, so two custom `PatternRecognizer`s (`IN_PAN`, `IN_AADHAAR`) were
registered on the same `AnalyzerEngine` rather than building a parallel regex path.

**Known issue hit and fixed -- G3 threshold.** SPEC's `OUT_OF_SCOPE_THRESHOLD` default (0.25)
was measured against the real corpus centroid and never fires: cosine similarity to the
centroid ran **0.42-0.72 across BOTH in-scope and clearly off-topic queries** with
`BAAI/bge-small-en-v1.5` (`"what's the weather in Pune?"` scored 0.53 -- above 0.25).
Recalibrated default to **0.6** in `config.py`/`.env`/`.env.example`, which routes the
genuinely ambiguous middle of that range to the LLM tiebreak instead of a cosine cutoff
that couldn't discriminate on its own for this embedding model.

### ✅ 4.4 — G5 output PII · 4.5 — G6 groundedness · 4.6 — G7 citation presence

**Known issue hit and fixed -- G5 scope.** SPEC says G5's trigger is "any entity." Applied
literally, Presidio's `DATE_TIME` and `LOCATION` recognizers fire on essentially every
sentence of PKC's own corpus (a holiday-calendar answer *is* dates; an office-FAQ answer
*is* locations) -- redacting them stripped the actual verifiable facts out of correct
answers and caused G6 to score a fully-cited, correct answer as ungrounded. Narrowed G5's
entity scope to person/account/ID-shaped entities (broader than G2, but not Presidio's
literal "everything") -- documented as a deliberate deviation, not a silent skip.

**Known issue hit and fixed -- citation markers vs. output-PII redaction.** Presidio's
`IP_ADDRESS` recognizer matches our `doc_id::cNN` chunk suffix as IPv6 zero-compression
shorthand (`"2026::c02"` parses the same shape as `"2001:db8::1"`), so G5 was redacting
*inside* citation markers and corrupting them. Fixed by excluding any detected entity whose
span overlaps a citation-marker match from G5's redaction (`pii.py`'s `protect_citations`).

**Known issue hit and fixed -- Unicode hyphens in citation markers.** Live-tested question
came back cited as `【co‑holiday‑calendar‑2026::c02】` using U+2011 NON-BREAKING HYPHEN
throughout instead of ASCII `-` -- same failure shape as the fullwidth-bracket tolerance
from Phase 3 (a correctly-cited, grounded answer silently becoming a false refusal).
`generate.py`'s `CITATION_RE` now accepts a small set of Unicode hyphen look-alikes, and
`_parse_citations` normalizes them back to ASCII before resolving against real `chunk_id`s.

**Refactor: G7's "regenerate once, then suppress" moved out of `generate.py`.** Phase 3's
`generate_answer()` used to silently collapse a zero-citation answer straight to
`REFUSAL_TEMPLATE`. That made G7's regenerate-once step unreachable (by the time the
pipeline saw the result it was already an unconditional refusal), so the collapse was
removed from `generate.py` and the retry-then-suppress policy now lives in
`pipeline.py::_postprocess`, which is what task 4.6 actually asks for.

**Latency delta (measured, `run_pipeline`'s per-stage timer, 3 runs):** G6 groundedness
itself adds **~250-360ms** per request (isolated Groq judge-call latency). End-to-end
wall-clock delta with the flag on vs. off is much noisier (~9s in one run) because
`GROQ_MAX_CONCURRENCY=2` serializes/queues the extra judge call behind whatever else is
in flight -- the per-stage number above is the trustworthy one for an "adds ~300ms"
interview answer.

### ✅ 4.7 — `app/guardrails/pipeline.py`
Ordered, short-circuiting, fail-closed. Fail-closed enforced in exactly ONE place
(`run_pipeline`/`_postprocess` wrap every stage call in `try/except Exception`) so
individual guardrail modules just do their real work and let failures propagate.
G4 budget is a pure function (`check_budget`) taking `tokens_used_today` as a parameter --
SPEC §5.4's `request_ledger` table doesn't exist until Phase 6, so `main.py` currently
passes `tokens_used_today=0` (never blocks yet) with that gap called out explicitly in
both files. Wired into `POST /api/chat` (`main.py`), replacing the direct
`retrieve()`/`generate_answer()` calls from Phase 3 -- guardrails weren't a phase-4
deliverable if nothing in the live request path actually calls them.

**Verify (actual):** `pytest tests/ -v` → **93 passed** (70 pre-existing + 23 new guardrail
tests across `test_guardrail_{injection,pii,scope,budget,groundedness,citations,pipeline}.py`
-- 7 guardrails, each with a unit test, plus pipeline integration tests). Live-tested
against the real HTTP API (`uvicorn` + `Invoke-RestMethod` as `ravi@pkc.com`/employee):
a direct injection → `guardrail_verdict: "blocked_injection"`; a question containing a
name + PAN → `input_pii_redacted: true`, answered normally, correctly cited,
`faithfulness_score: 0.8`; `"What is the weather in Pune?"` →
`guardrail_verdict: "blocked_out_of_scope"`. Fail-closed confirmed via
`test_pipeline_fails_closed_when_a_stage_raises` (monkeypatches G1 to raise ⇒ pipeline
returns `blocked_injection`, never `allowed`).

**Phase 4 exit gate:** 7 guardrail unit tests pass; fail-closed verified; pipeline wired
into the live `/api/chat` path and smoke-tested end-to-end. **Verified 2026-08-14.**

---

## Phase 5 — Evals & CI

**Goal:** every deploy gated on measured security.

### 5.1 — `data/golden/quality.yaml` — 80 per-role Q&A pairs
Tedious; do it in two sittings. Skipping this makes the whole project unverifiable.

### 5.2 — `data/golden/security.yaml` — 45 cases
**Must include ~10 overlap positives** (SPEC §7.2). A suite that only tests refusals rewards
a system that refuses everything.

### 5.3 — `data/golden/adversarial.yaml` — 30 cases
Include indirect injection via the poisoned corpus document.

### 5.4 — `evals/run_evals.py`
Ragas harness, judge LLM on Groq, **concurrency ≤ 2 with backoff**, cache judgments by
content hash.

### 5.5 — 25-doc fixture corpus for CI
Full corpus is too slow for a PR gate. Fixture must still contain all 5 deliberate cases.

### 5.6 — `.github/workflows/evals.yml`
Per SPEC §7.4. Hard gates + regression gate vs `evals/results/baseline.json`. PR comment with results.

### 5.7 — Baseline
Record `evals/results/baseline.json` on `main` so regressions are measurable.
**Must be captured with the same `--fixture-docs data/golden/fixture_docs.txt` scope
CI uses** — comparing a 25-doc-fixture PR run against an unscoped full-100-doc/155-case
baseline would compare different case populations and could flag spurious "regressions"
from sampling noise alone, not real drops. Ingest the fixture into a scratch Qdrant
collection (not the dev collection holding the full corpus) before running
`--save-baseline`, so local dev state isn't disturbed either.

**Status as of 2026-08-16: full pipeline run completed (quota recovered after the
2026-08-15 exhaustion). Two eval findings surfaced and were investigated:**

1. **Fixed -- `score_security()` false-positive leaks.** The real 2026-08-16 run flagged
   `leak_rate=0.0488` (SEC-021, SEC-023). Investigated by hand: both cases' actual retrieved
   contexts (from `run_cache.json`) confirm the ACL filter correctly excluded the restricted
   doc every time (`sales-gtm-strategy-2026`, `exec-restructuring-eng-division` never
   retrieved) -- the model answered from OTHER, legitimately-authorized documents that
   happen to overlap in topic (e.g. a public product roadmap also discusses 2026 strategy).
   Read both full answers by eye against `must_not_contain` -- zero forbidden strings, no
   paraphrase either. The bug was in the eval, not the pipeline: `score_security()` counted
   *any* non-refusal-template answer as a leak, not just ones containing forbidden content.
   Fixed: a `expect: refusal` case is now only a leak if `leaked_strings` is non-empty;
   non-leaking non-refusals are reported separately as `non_refusal_clean` (visible, not
   silently dropped) instead of failing the hard gate. Re-scored against the same cached
   `run_cache.json` data (no new Groq calls) -- confirmed `leak_rate` drops to `0.0`.

2. **OPEN -- real false-refusal bug, `false_refusal_rate=0.875` (7/8 "expect: answer"
   security cases -- corrected 2026-08-17; the first `0.1707` figure divided by all 41
   scored cases including 33 refusal-type ones that can't produce a false refusal, which
   diluted it ~5x. Same fix applied to `leak_rate`'s denominator for consistency, though
   it read correctly either way since `leaks` was 0.)**
   SEC-038 through SEC-045 (arjun/karan/divya asking about `cloud_costs`/`marketing_spend`
   docs they ARE authorized for via the overlap-role rules) get `verdict=blocked_ungrounded`
   instead of a real, cited answer, while the near-identical SEC-037 (same user, same doc
   class, different specific doc) succeeds cleanly. What's ruled out: not a retrieval/ACL
   bug in the sense of "wrong docs excluded" -- `app/guardrails/pipeline.py`'s `_refused()`
   helper doesn't pass `hits=hits` through, so every blocked verdict's `CaseRun.contexts`
   reads empty regardless of what was actually retrieved; that emptiness is NOT evidence
   retrieval failed, just an artifact of how the refusal path reports its result. **Fix
   applied 2026-08-17 (zero Groq cost, pure code change):** `PipelineResult` now carries a
   `block_reason: str | None` field, and `_refused()` accepts `block_reason=` + `hits=` so
   G5/G6/G7 blocks each record which stage fired and (for G6) the actual groundedness
   score, instead of all three being indistinguishable behind one REFUSAL_TEMPLATE. Next
   step: re-run just SEC-038/039/040/041/042/044/045 (7 cases, cheap) once there's a small
   quota window, and the cached `CaseRun.block_reason` will say definitively whether it's
   G6 or G7 and why.

Prior infra work (still true, not re-explained here): `evals/run_evals.py` is resilient
(per-case error isolation, resumable `run_cache.json`), the NaN-judge-caching bug is fixed,
and `scripts/select_baseline_subset.py` exists as a fallback for future quota crunches.

This baseline was saved WITH the known false-refusal bug in it (finding 2 above), on
purpose -- CLAUDE.md: never hide a known issue behind a falsely-clean number. The next
baseline, once finding 2 is fixed, should show `false_refusal_rate` drop and that
improvement will register as a (good) baseline change, not a silent one.

**3. OPEN -- quality suite has zero real signal in this baseline.** All 30 fixture-scoped
pipeline calls succeeded (`citation_hit_rate=0.7667` proves generation is working), but
every one of the 30 Ragas judge calls hit the same Groq TPD wall, so `context_precision`
/`context_recall`/`faithfulness`/`answer_relevancy` are all `0.0` -- an artifact of 100%
judge failure, not real scores. `compare_to_baseline()`'s regression check can't flag a
real quality drop against a `0.0` floor (nothing regresses below zero), so **this baseline
gives no quality regression protection until it's re-run with headroom for the Ragas judge
calls specifically** (`evals/run_evals.py --suite quality --fixture-docs
data/golden/fixture_docs.txt --save-baseline` once quota allows -- security/adversarial
don't need re-running, `compare_to_baseline` only reads the `quality` sub-object).
`security` (`leak_rate=0.0`, real) and `adversarial` (`injection_block_rate=1.0`, real) ARE
trustworthy in this baseline.

**Verify (the important one):** open a deliberately-broken PR that removes the ACL filter and
**watch CI fail**. Screenshot it. A red CI run catching a real security regression is more
persuasive than a green one.

**Phase 5 exit gate:** CI green on `main`; leak_rate 0; injection ≥ 0.95; faithfulness ≥ 0.85;
broken-PR test goes red. Tag `v0.6-evals`.

---

## Phase 6 — UI, observability, deploy

**Goal:** publicly reachable, traced, documented.

### 6.1 — `ui/app.py` (Streamlit)
Light theme, left sidebar nav (Ask PKC / History / Dashboard / Security events), role badge
pinned bottom-left, expandable citations, inline banner when a guardrail fires
(**show why** — that detail reads as maturity). A rendered HTML mockup of the target design
exists; match its structure and hierarchy.

### 6.2 — Admin dashboard (`c_level` only)
SPEC §10 panels. Lead with the `leak_rate` stat tile.

### 6.3 — LangSmith wiring
Spans per stage, tagged by role and verdict.

### 6.4 — Ledger + shadow cost
SPEC §5.4.

### 6.5 — Deploy
UI → Streamlit Community Cloud. API → HF Spaces (Docker) or Render. Qdrant → Qdrant Cloud
free cluster. Secrets via platform env vars, never committed.

### 6.6 — Docs
`README.md` (SPEC §13 positioning, architecture diagram, metrics table, 90s demo GIF),
`docs/DESIGN_DECISIONS.md`, `docs/AZURE_DEPLOYMENT.md`, `docs/FREE_TIER_NOTES.md`.

**Phase 6 exit gate:** a stranger with the URL logs in as three roles, asks the same question,
gets three different outcomes, and the README explains why in under 60 seconds. Tag `v1.0`.

---

## The demo script (rehearse; record as GIF)

| Time | Action | Point |
|---|---|---|
| 0:00 | `meera@pkc.com` (c_level): *"What was our Q3 2025 net revenue?"* → cited answer | It works |
| 0:20 | `ravi@pkc.com` (employee): **identical** question → refusal | Same question, different identity |
| 0:35 | LangSmith traces side by side: 8 chunks retrieved vs **0** | Enforced at retrieval, not by model judgment |
| 0:50 | As Ravi: *"Ignore previous instructions…"* → blocked, banner | Injection defense |
| 1:05 | `arjun@pkc.com` (finance): AWS spend → **answers** (overlap) | Precise, not blanket denial |
| 1:20 | Admin dashboard: **leak_rate 0**, shadow cost | Measured, not asserted |

The pivot at 0:35 is where a technical reviewer decides whether you understand the problem.

---

## If you fall behind — cut in this order

**Cut first:** hybrid sparse retrieval (dense-only is fine) · conversation memory ·
admin dashboard (a `metrics.md` works) · G3 out-of-scope · shadow cost charting.

**Cut only if desperate:** cloud deployment (a great GIF + clean local setup beats a broken
deploy) · G6 groundedness · corpus down to 50 docs.

**Never cut:** server-side ACL filtering · the security eval suite · leak_rate = 0 ·
the anti-pattern tests · the demo GIF · a README leading with the security result.

Everything in "never cut" is the project's thesis. The rest is decoration on top of it.

---

## Final task — `docs/DESIGN_DECISIONS.md`

Five entries, each: *decision · alternatives considered · why · what I'd change at scale.*

1. Server-side ACL filtering vs post-filter vs collection-per-role
2. Chunk-level ACLs vs document-level
3. Denormalized `allowed_roles` vs joining a permissions service
4. Dedicated injection classifier vs prompt hardening
5. Groundedness checking vs accepting hallucination risk

Write this **during** the build while reasoning is fresh, not six months later.
