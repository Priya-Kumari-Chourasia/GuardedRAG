"""
Produces data/golden/baseline_subset.txt -- a ~29-case allowlist for evals/run_evals.py's
--case-ids flag.

Why this exists: PLAN.md task 5.7 (record evals/results/baseline.json) hit Groq's free-tier
daily token limit (TPD) repeatedly -- the full 104-case fixture-scoped run needs more
sustained headroom than the rolling 24h window was giving on the day this was run. Rather
than either (a) violate CLAUDE.md's "free tier only, no credit card" rule, or (b) block
indefinitely, this is a deliberately-chosen SMALLER subset that still exercises everything
that actually matters for a first baseline:

  - All 5 SPEC Sec 8 deliberate corpus cases (cross-ref, conflicting versions, near-dup,
    poisoned doc, synthetic PII) -- see the category/attack_type filters below.
  - Every security overlap-positive case (SPEC Sec 7.2's whole point: a suite that only
    tests refusals rewards a system that refuses everything).
  - All 6 adversarial attack_types represented, not just a couple.

This is an explicit, documented trade-off, not a silent shortcut (CLAUDE.md: never mark
something complete if it was silently skipped) -- the resulting baseline covers less
ground than the full 104-case fixture run, and PLAN.md/task notes should say so. The
harness's run_cache.json means nothing computed here is wasted when the full 104-case
baseline is eventually captured later (a low-priority, non-blocking background effort).
"""

from __future__ import annotations

from pathlib import Path

import yaml

GOLDEN_DIR = Path(__file__).resolve().parent.parent / "data" / "golden"


def _load(suite: str) -> list[dict]:
    with open(GOLDEN_DIR / f"{suite}.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _fixture_docs() -> set[str]:
    lines = (GOLDEN_DIR / "fixture_docs.txt").read_text(encoding="utf-8").splitlines()
    return {line.strip() for line in lines if line.strip() and not line.strip().startswith("#")}


def _fixture_ok(case: dict, fixture: set[str]) -> bool:
    return set(case.get("must_cite", [])) <= fixture


def main() -> None:
    quality = _load("quality")
    security = _load("security")
    adversarial = _load("adversarial")
    fixture = _fixture_docs()

    # Quality: SPEC Sec 8 deliberate cases (cross_ref, conflicting_versions, near_dup)
    # plus a handful of standard cases for a general quality-metric baseline.
    quality_special = ["Q-051", "Q-049", "Q-050", "Q-014"]
    quality_standard = sorted(
        c["id"] for c in quality if c.get("category") == "standard" and _fixture_ok(c, fixture)
    )[:4]
    quality_ids = quality_special + quality_standard

    # Security: EVERY overlap-positive case (must include all -- CLAUDE.md's explicit
    # warning about eval suites that only test refusals) plus a handful of refusal
    # cases for a basic leak_rate signal.
    sec_answer = sorted(c["id"] for c in security if c["expect"] == "answer" and _fixture_ok(c, fixture))
    sec_refusal = sorted(c["id"] for c in security if c["expect"] == "refusal")[:5]
    security_ids = sec_answer + sec_refusal

    # Adversarial: all 6 attack_types represented. Extra weight on indirect_injection
    # (the poisoned document -- deliberate case 4) and pii_extraction (deliberate case 3).
    by_type: dict[str, list[str]] = {}
    for c in adversarial:
        by_type.setdefault(c["attack_type"], []).append(c["id"])
    adversarial_ids = (
        sorted(by_type["indirect_injection"])[:2]
        + sorted(by_type["pii_extraction"])[:1]
        + sorted(by_type["direct_injection"])[:1]
        + sorted(by_type["encoded_instruction"])[:1]
        + sorted(by_type["multiturn_poisoning"])[:1]
        + sorted(by_type["roleplay_jailbreak"])[:1]
    )

    out_path = GOLDEN_DIR / "baseline_subset.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# scripts/select_baseline_subset.py output -- PLAN.md 5.7 quota-constrained baseline\n")
        f.write("# One line per case: <suite>:<case_id>\n")
        for cid in quality_ids:
            f.write(f"quality:{cid}\n")
        for cid in security_ids:
            f.write(f"security:{cid}\n")
        for cid in adversarial_ids:
            f.write(f"adversarial:{cid}\n")

    total = len(quality_ids) + len(security_ids) + len(adversarial_ids)
    print(f"quality: {len(quality_ids)}, security: {len(security_ids)}, "
          f"adversarial: {len(adversarial_ids)} -- total {total}")
    print(f"written {out_path}")


if __name__ == "__main__":
    main()
