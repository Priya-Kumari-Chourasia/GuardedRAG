"""
Formats evals/results/latest.json (written by evals/run_evals.py) into a Markdown
PR comment body -- PLAN.md task 5.6 / SPEC_1.md Sec 7.4 ("post results as a PR
comment"). Kept as a small, readable script instead of inline JS in the workflow
YAML, matching this project's convention that non-obvious logic lives in a
reviewable .py file.

Usage: python -m evals.format_pr_comment evals/results/latest.json > comment.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ICON = {True: "PASS", False: "FAIL"}


def _suite_line(name: str, data: dict) -> str:
    icon = _ICON[data.get("gate_pass", False)]
    if name == "security":
        detail = f"leak_rate={data['leak_rate']}, false_refusal_rate={data['false_refusal_rate']}"
    elif name == "adversarial":
        detail = f"injection_block_rate={data['injection_block_rate']}"
    elif name == "quality":
        coverage = data.get("metric_coverage") or {}
        metrics = ", ".join(
            f"{m}={data[m]} (n={coverage.get(m, '?')})"
            for m in ("context_precision", "context_recall", "faithfulness", "answer_relevancy")
        )
        detail = metrics
    else:
        detail = ""
    n_errors = len(data.get("errors") or [])
    if n_errors:
        detail += f" ({n_errors} errored -- excluded from n/gate, see below)"
    return f"| {name} | {data.get('n', '?')} | {detail} | **{icon}** |"


def format_comment(report: dict) -> str:
    overall = _ICON[report.get("overall_gate_pass", False)]
    lines = [
        "## Eval results -- SPEC_1.md Sec 7 CI gate",
        "",
        f"**Overall: {overall}**  (run at {report.get('run_at', '?')})",
        "",
        "| suite | n | metrics | gate |",
        "|---|---:|---|---|",
    ]
    for suite in ("security", "adversarial", "quality"):
        if suite in report.get("suites", {}):
            lines.append(_suite_line(suite, report["suites"][suite]))

    regressions = report.get("regressions_vs_baseline") or []
    if regressions:
        lines += ["", "**Regressions vs baseline (>5% drop):**", ""]
        for r in regressions:
            lines.append(f"- `{r['metric']}`: {r['baseline']} -> {r['current']} ({r['drop_pct']}% drop)")

    security = report.get("suites", {}).get("security", {})
    if security.get("leaks"):
        lines += ["", f"**{len(security['leaks'])} security leak(s) -- SPEC I10 hard gate (leak_rate == 0):**", ""]
        for leak in security["leaks"][:10]:
            lines.append(f"- `{leak['id']}`")

    adversarial = report.get("suites", {}).get("adversarial", {})
    if adversarial.get("not_blocked"):
        lines += ["", f"**{len(adversarial['not_blocked'])} adversarial case(s) not blocked:**", ""]
        for nb in adversarial["not_blocked"][:10]:
            lines.append(f"- `{nb['id']}` ({nb['reason']})")

    if report.get("had_errors"):
        lines += ["", "**Infra errors (e.g. Groq rate limits) -- excluded from scoring, not a gate verdict:**", ""]
        for suite, data in report.get("suites", {}).items():
            for err in (data.get("errors") or [])[:10]:
                lines.append(f"- `{suite}/{err['id']}`: {err['error'][:200]}")
        lines.append("")
        lines.append("_Re-push to retry -- errored cases are the only ones re-run; "
                      "successes are cached (see evals/results/run_cache.json)._")

    lines += ["", "_Fixture run: 25-doc CI corpus, cases scoped via data/golden/fixture_docs.txt "
                    "(see scripts/select_fixture_docs.py). Full 100-doc/155-case run happens on `main`._"]
    return "\n".join(lines)


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("evals/results/latest.json")
    if not path.exists():
        # The eval suite never ran -- e.g. `pytest tests/` failed first (the CI
        # workflow's steps after it still fire via `if: always()` so the PR gets
        # a comment either way). Report that plainly instead of crashing here:
        # an uncaught exception left `pr_comment.md` empty, which made the next
        # step's `gh pr comment --body-file` call fail with GraphQL's
        # "Body cannot be blank" -- a second, confusing failure on top of the
        # real one. Found via the PLAN.md 5.7 broken-ACL-filter verify PR.
        print("## Eval results -- SPEC_1.md Sec 7 CI gate\n\n"
              "**Overall: FAIL** -- the eval suite never ran because an earlier "
              "step (`pytest tests/`) failed first. See that step's log for the "
              "real failure.")
        return
    report = json.loads(path.read_text(encoding="utf-8"))
    print(format_comment(report))


if __name__ == "__main__":
    main()
