"""
One-off analysis script behind data/golden/fixture_docs.txt (PLAN.md task 5.5).

Not run in CI -- this is the record of HOW the 25-doc fixture was chosen, so the
choice can be re-derived (or redone) if the golden sets or corpus change, instead
of the list just being 25 doc_ids with no traceable reasoning.

Two selections are printed:
  1. A pure greedy set-cover over "how many doc-dependent golden cases become
     answerable" -- included to show why it was REJECTED: it dumps the whole
     budget into cheap 1-doc company-wide cases and ends up with near-zero
     department/ACL diversity, which is useless for a fixture whose entire job
     is exercising cross-role and overlap authorization.
  2. The curated, department-balanced selection actually written to
     data/golden/fixture_docs.txt.

A case only NEEDS its docs present to remain a valid CI signal if it expects an
ANSWER (quality.yaml cases, security.yaml's "expect: answer" overlap-positives).
Refusal-type security cases and all adversarial cases stay valid no matter which
docs are ingested: app/guardrails/pipeline.py's I4 zero-hits refusal returns the
same byte-identical REFUSAL_TEMPLATE as an ACL refusal (see pipeline.py:214), so
a missing cited doc can only ever make a refusal case's signal weaker, never
manufacture a false leak or a false pass.
"""

from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path

import yaml

GOLDEN_DIR = Path(__file__).resolve().parent.parent / "data" / "golden"

MANDATORY = {
    # SPEC Sec 8 deliberate case 1: cross-reference
    "fin-vendor-aws", "eng-cloud-costs-q3-2025",
    # deliberate case 2: conflicting versions
    "fin-q3-2025-forecast", "fin-q3-2025-report",
    # deliberate case 3: synthetic PII (representative doc; several others qualify)
    "hr-emp-record-arjun",
    # deliberate case 4: poisoned document
    "eng-postmortem-embedding-latency",
    # deliberate case 5: near-duplicate at different sensitivities
    "co-allhands-2025-09", "exec-board-deck-sep-special",
}

CURATED = {
    # company_wide (4)
    "co-allhands-2025-09", "co-handbook-2026", "co-org-chart-q3-2025", "co-roadmap-h1-2026",
    # hr (4)
    "hr-emp-record-arjun", "hr-payroll-2025-08", "hr-perf-review-neha", "hr-comp-bands-eng",
    # finance (5)
    "fin-q3-2025-forecast", "fin-q3-2025-report", "fin-vendor-aws", "fin-q4-2025-report", "fin-budget-2025",
    # sales_marketing (4)
    "sales-marketing-spend-q3-2025", "sales-digital-ad-spend-q3-2025",
    "sales-pipeline-q3-2025", "sales-gtm-strategy-2026",
    # engineering (5)
    "eng-cloud-costs-q3-2025", "eng-postmortem-embedding-latency",
    "eng-cloud-costs-aws-breakdown-sep", "eng-cloud-costs-optimization-q4", "eng-architecture-authz",
    # executive (3)
    "exec-board-deck-sep-special", "exec-board-deck-q3-2025", "exec-strategy-2026-priorities",
}


def _load(suite: str) -> list[dict]:
    with open(GOLDEN_DIR / f"{suite}.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _doc_dependent_cases() -> list[tuple[str, set[str]]]:
    quality = _load("quality")
    security = _load("security")
    cases = [(c["id"], set(c["must_cite"])) for c in quality]
    cases += [(c["id"], set(c["must_cite"])) for c in security if c["expect"] == "answer"]
    return cases


def _covered(cases: list[tuple[str, set[str]]], selection: set[str]) -> set[str]:
    return {cid for cid, docs in cases if docs <= selection}


def _greedy_set_cover(cases: list[tuple[str, set[str]]], mandatory: set[str], budget: int) -> set[str]:
    selection = set(mandatory)
    while len(selection) < budget:
        base = len(_covered(cases, selection))
        best_doc, best_gain = None, 0
        for _, docs in cases:
            for d in docs - selection:
                gain = len(_covered(cases, selection | {d})) - base
                if gain > best_gain:
                    best_doc, best_gain = d, gain
        if best_doc is None:
            break
        selection.add(best_doc)
    return selection


def _department_spread(selection: set[str]) -> dict[str, int]:
    spec = importlib.util.spec_from_file_location(
        "corpus_manifest", Path(__file__).resolve().parent / "corpus_manifest.py"
    )
    cm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cm)  # type: ignore[union-attr]
    spread: Counter[str] = Counter()
    for entry in cm.MANIFEST:
        if entry["doc_id"] in selection:
            spread[entry["department"]] += 1
    return dict(spread)


def main() -> None:
    quality = _load("quality")
    security = _load("security")
    adversarial = _load("adversarial")
    cases = _doc_dependent_cases()

    greedy = _greedy_set_cover(cases, MANDATORY, budget=25)
    print(f"[rejected] pure greedy: {len(_covered(cases, greedy))}/{len(cases)} doc-dependent cases covered")
    print(f"           department spread: {_department_spread(greedy)}")
    print()

    assert len(CURATED) == 25, len(CURATED)
    assert MANDATORY <= CURATED, MANDATORY - CURATED

    sec_answer = [c for c in security if c["expect"] == "answer"]
    sec_refusal = [c for c in security if c["expect"] == "refusal"]
    q_ok = sum(1 for c in quality if set(c["must_cite"]) <= CURATED)
    sec_ok = sum(1 for c in sec_answer if set(c["must_cite"]) <= CURATED)

    print(f"[chosen] curated 25-doc fixture: {q_ok}/{len(quality)} quality cases answerable")
    print(f"         {sec_ok}/{len(sec_answer)} security overlap-positive cases answerable")
    print(f"         {len(sec_refusal)}/{len(sec_refusal)} security refusal cases valid regardless")
    print(f"         {len(adversarial)}/{len(adversarial)} adversarial cases valid regardless")
    print(f"         department spread: {_department_spread(CURATED)}")


if __name__ == "__main__":
    main()
