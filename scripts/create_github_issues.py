#!/usr/bin/env python3
"""Create Parallax GitHub roadmap issues with labels and milestones."""

from __future__ import annotations

import json
import subprocess
from typing import Sequence

REPO = "askmy-stack/parallax"


def run(cmd: list[str]) -> str:
    out = subprocess.check_output(cmd, text=True)
    return out.strip()


def gh(*args: str) -> str:
    return run(["gh", *args])


def add_labels(number: int, labels: Sequence[str]) -> None:
    if not labels:
        return
    cmd = ["gh", "issue", "edit", str(number), "--repo", REPO]
    for lab in labels:
        cmd.extend(["--add-label", lab])
    subprocess.check_call(cmd)


def create_issue(
    title: str,
    milestone: str,
    labels: Sequence[str],
    body: str,
    *,
    close: bool = False,
) -> int:
    cmd = [
        "gh",
        "issue",
        "create",
        "--repo",
        REPO,
        "--title",
        title,
        "--milestone",
        milestone,
        "--body",
        body,
    ]
    for lab in labels:
        cmd.extend(["--label", lab])
    url = run(cmd)
    number = int(url.rstrip("/").split("/")[-1])
    if close:
        gh(
            "issue",
            "close",
            str(number),
            "--repo",
            REPO,
            "--reason",
            "completed",
            "--comment",
            "Completed in vertical slice on main.",
        )
    print(f"{'CLOSED' if close else 'OPEN  '} #{number} {title}")
    return number


DONE = """## Context
Completed as part of the first **tool-semantic-drift** vertical slice (`tool-semantic-drift-001`).

## Acceptance
- Covered by `make ci` and `experiments/results/tool-semantic-drift-001.md`

## Notes
Tracking issue closed to keep the board accurate.
"""

SECTION = """## Why
{why}

## Scope
{scope}

## Acceptance criteria
{acceptance}

## References
- Roadmap: `docs/roadmap.md`
- Related vertical slice: `experiments/results/tool-semantic-drift-001.md`
"""


def body(why: str, scope: str, acceptance: str) -> str:
    return SECTION.format(why=why, scope=scope, acceptance=acceptance)


def main() -> None:
    # Label already-closed issues #1-8
    closed_labels = {
        1: [
            "type:benchmark",
            "area:agentfailbench",
            "priority:P0",
            "size:M",
            "vertical-slice",
            "enhancement",
        ],
        2: [
            "type:benchmark",
            "area:agentfailbench",
            "priority:P0",
            "size:S",
            "vertical-slice",
            "enhancement",
        ],
        3: [
            "type:benchmark",
            "area:agentfailbench",
            "priority:P0",
            "size:M",
            "vertical-slice",
            "enhancement",
        ],
        4: [
            "type:runtime",
            "area:tracing",
            "priority:P0",
            "size:M",
            "vertical-slice",
            "enhancement",
        ],
        5: [
            "type:baselines",
            "area:detector",
            "priority:P0",
            "size:M",
            "vertical-slice",
            "enhancement",
        ],
        6: [
            "type:runtime",
            "area:diagnosis",
            "priority:P0",
            "size:S",
            "vertical-slice",
            "enhancement",
        ],
        7: ["type:recovery", "priority:P0", "size:M", "vertical-slice", "enhancement"],
        8: [
            "type:research",
            "area:release",
            "priority:P0",
            "size:S",
            "vertical-slice",
            "documentation",
        ],
    }
    for num, labels in closed_labels.items():
        add_labels(num, labels)
        print(f"Labeled #{num}")

    # Re-open M0 briefly isn't needed; create closed M0 under M1 docs or skip.
    # Create open M0 tracker on closed milestone via API if needed — skip.

    open_issues: list[tuple[str, str, list[str], str]] = [
        # ---- M1 ----
        (
            "[M1] Implement deterministic database task environment",
            "M1 — Minimal agent environment",
            [
                "type:benchmark",
                "area:agentfailbench",
                "priority:P0",
                "size:L",
                "enhancement",
            ],
            body(
                "Roadmap Milestone 1 requires a second deterministic environment beyond the customer API.",
                "- In-memory SQL (sqlite) investigation tasks\n"
                "- Action/observation interface consistent with `TaskSpec` / `Action` / `EnvObservation`\n"
                "- At least one success validator",
                "- [ ] Environment package under `agentfailbench/environments/`\n"
                "- [ ] Unit tests for normal (non-failure) success path\n"
                "- [ ] Documented in README repo map",
            ),
        ),
        (
            "[M1] Expand to five normal tasks with success validators",
            "M1 — Minimal agent environment",
            [
                "type:benchmark",
                "area:agentfailbench",
                "priority:P0",
                "size:L",
                "enhancement",
            ],
            body(
                "Only `update_customer_subscription` exists; Milestone 1 targets five normal tasks.",
                "- Add 4 additional tasks across API and/or DB envs "
                "(e.g. lookup, transform, multi-step API, data-quality check)\n"
                "- Each task has a deterministic success validator\n"
                "- Register cases in AgentFailBench registry",
                "- [ ] Five tasks runnable without failure injection\n"
                "- [ ] Validators covered by tests\n"
                "- [ ] Case YAML or registry entries for each",
            ),
        ),
        (
            "[M1] Formalize shared task interface across environments",
            "M1 — Minimal agent environment",
            [
                "type:benchmark",
                "area:agentfailbench",
                "priority:P1",
                "size:M",
                "enhancement",
                "good first issue",
            ],
            body(
                "Customer API works, but env protocol should be explicit for new environments.",
                "- Protocol/ABC for `reset`, `step`, `validate_success`\n"
                "- Shared docs in `docs/benchmark-specification.md`",
                "- [ ] Protocol implemented and used by customer_api (+ stub for DB)\n"
                "- [ ] mypy-clean",
            ),
        ),
        # ---- M2 ----
        (
            "[M2] Define shared failure injector interface",
            "M2 — Failure injection",
            [
                "type:benchmark",
                "area:agentfailbench",
                "priority:P0",
                "size:S",
                "enhancement",
                "good first issue",
            ],
            body(
                "SemanticDriftInjector works ad hoc; suites need a common interface.",
                "- `before_step` / `after_step` / `reset` protocol\n"
                "- Wire through `runners/episode.py`",
                "- [ ] Interface + adapter for existing SemanticDriftInjector\n"
                "- [ ] Tests for registration/dispatch",
            ),
        ),
        (
            "[M2] Implement tool timeout failure injector",
            "M2 — Failure injection",
            [
                "type:benchmark",
                "area:agentfailbench",
                "priority:P1",
                "size:M",
                "enhancement",
            ],
            body(
                "ToolDrift suite needs timeout cases with ground-truth labels.",
                "- Inject latency/timeout at trigger step\n"
                "- Case YAML + labels\n"
                "- Visible vs invisible timeout variants optional",
                "- [ ] Injector + case file\n"
                "- [ ] Episode runner support\n"
                "- [ ] Unit test",
            ),
        ),
        (
            "[M2] Implement schema drift failure injector",
            "M2 — Failure injection",
            [
                "type:benchmark",
                "area:agentfailbench",
                "priority:P1",
                "size:M",
                "enhancement",
            ],
            body(
                "Complement semantic drift with schema-level contract breaks.",
                "- Rename/remove fields while keeping HTTP success where applicable\n"
                "- Ground-truth first_detectable / final_failure steps",
                "- [ ] Injector + YAML case\n"
                "- [ ] Tests",
            ),
        ),
        (
            "[M2] Implement stale memory failure injector",
            "M2 — Failure injection",
            [
                "type:benchmark",
                "area:agentfailbench",
                "priority:P0",
                "size:L",
                "enhancement",
            ],
            body(
                "MemoryGuard suite — next vertical slice after tool semantic drift.",
                "- Persistent memory with outdated API/plan fact\n"
                "- Ground-truth root cause `stale_memory`\n"
                "- Prefer vertical-slice workflow (trace → detect → diagnose → recover)",
                "- [ ] Memory store + injector\n"
                "- [ ] Case YAML\n"
                "- [ ] Minimal detector signal for conflict with live tool metadata",
            ),
        ),
        (
            "[M2] Implement conflicting memory failure injector",
            "M2 — Failure injection",
            [
                "type:benchmark",
                "area:agentfailbench",
                "priority:P1",
                "size:M",
                "enhancement",
            ],
            body(
                "MemoryGuard suite needs conflicting entries.",
                "- Two memory records disagree on the same key\n"
                "- Ground-truth labels",
                "- [ ] Injector + case\n"
                "- [ ] Tests",
            ),
        ),
        (
            "[M2] Implement stale retrieval failure injector",
            "M2 — Failure injection",
            [
                "type:benchmark",
                "area:agentfailbench",
                "priority:P1",
                "size:M",
                "enhancement",
            ],
            body(
                "Data & Retrieval suite — outdated documents still ranked highly.",
                "- Retrieval corpus with stale doc injected at trigger step\n"
                "- Ground-truth labels",
                "- [ ] Injector + case\n"
                "- [ ] Tests",
            ),
        ),
        (
            "[M2] Implement planning loop / no-progress failure injector",
            "M2 — Failure injection",
            [
                "type:benchmark",
                "area:agentfailbench",
                "priority:P1",
                "size:M",
                "enhancement",
            ],
            body(
                "Planning suite — agent oscillates without progress.",
                "- Force repeated subgoals / no-progress loop\n"
                "- Ground-truth first_detectable step",
                "- [ ] Injector + case\n"
                "- [ ] Compatible with no-progress detector (M4)",
            ),
        ),
        # ---- M3 ----
        (
            "[M3] Map semantic trace fields to OpenTelemetry GenAI conventions",
            "M3 — Semantic tracing",
            ["type:runtime", "area:tracing", "priority:P1", "size:L", "enhancement"],
            body(
                "Roadmap requires OTEL-compatible spans where practical.",
                "- Attribute mapping doc + exporter stub (OTLP optional)\n"
                "- Keep research-specific fields as extensions",
                "- [ ] Mapping table in docs\n"
                "- [ ] Optional OTLP export behind extra dependency\n"
                "- [ ] Tests for attribute presence",
            ),
        ),
        (
            "[M3] Export traces to Parquet for analysis",
            "M3 — Semantic tracing",
            ["type:runtime", "area:tracing", "priority:P1", "size:M", "enhancement"],
            body(
                "JSONL works; Parquet enables DuckDB/Pandas analysis at scale.",
                "- Optional `analysis` extra (pyarrow/pandas)\n"
                "- CLI flag `--format parquet|jsonl`",
                "- [ ] Parquet writer\n"
                "- [ ] Round-trip test when extras installed",
            ),
        ),
        (
            "[M3] Enrich goal-progress tracking and trace validation rules",
            "M3 — Semantic tracing",
            [
                "type:runtime",
                "area:tracing",
                "priority:P2",
                "size:M",
                "enhancement",
                "good first issue",
            ],
            body(
                "Basic progress exists; need stagnation/oscillation signals.",
                "- Progress deltas, repeated-action counters\n"
                "- Stricter validators for required semantic fields",
                "- [ ] Features exported on TraceEvent\n"
                "- [ ] Validation errors are actionable",
            ),
        ),
        # ---- M4 ----
        (
            "[M4] Rule-based no-progress detector baseline",
            "M4 — Detection baselines",
            [
                "type:baselines",
                "area:detector",
                "priority:P0",
                "size:M",
                "enhancement",
                "good first issue",
            ],
            body(
                "Needed for planning-loop failures and early stagnation.",
                "- Detect repeated actions / flat goal progress\n"
                "- Integrate into `all_detectors()` and experiment compare",
                "- [ ] Detector + unit tests\n"
                "- [ ] Appears in `ras experiment run --compare` output",
            ),
        ),
        (
            "[M4] Isolation Forest detection baseline",
            "M4 — Detection baselines",
            ["type:baselines", "area:detector", "priority:P1", "size:L", "enhancement"],
            body(
                "Classical anomaly baseline from roadmap §12 / Milestone 4.",
                "- Feature vectors from traces\n"
                "- Fit on clean runs; score drifted runs\n"
                "- Depends on `analysis` extra (sklearn)",
                "- [ ] Baseline module under `baselines/classical_ml/`\n"
                "- [ ] Documented limitations\n"
                "- [ ] Tests with synthetic features",
            ),
        ),
        (
            "[M4] Change-point detection baseline",
            "M4 — Detection baselines",
            ["type:baselines", "area:detector", "priority:P2", "size:M", "enhancement"],
            body(
                "Detect distribution shifts in telemetry/semantic features over steps.",
                "- Simple online/offline change-point on chosen series\n"
                "- Compare lead time vs semantic mismatch",
                "- [ ] Detector + tests\n"
                "- [ ] Result row in experiment report format",
            ),
        ),
        (
            "[M4] Embedding-distance detection baseline",
            "M4 — Detection baselines",
            ["type:baselines", "area:detector", "priority:P2", "size:L", "enhancement"],
            body(
                "Compare expectation vs observation text/structure embeddings.",
                "- Deterministic embedding stub acceptable for CI\n"
                "- Optional real model behind extra",
                "- [ ] Baseline API\n"
                "- [ ] CI uses stub; docs note optional model",
            ),
        ),
        (
            "[M4] Expand evaluation CLI (multi-case suite + metrics table)",
            "M4 — Detection baselines",
            ["type:baselines", "type:infra", "priority:P1", "size:M", "enhancement"],
            body(
                "`ras experiment run` handles one case; need suite mode.",
                "- `--suite tool_drift` runs all YAML under a folder\n"
                "- Aggregate detection lead time, FPR, recovery rate",
                "- [ ] Suite runner\n"
                "- [ ] Markdown/CSV summary artifact",
            ),
        ),
        # ---- M5 ----
        (
            "[M5] Formalize root-cause label schema",
            "M5 — Diagnosis",
            [
                "type:runtime",
                "area:diagnosis",
                "priority:P0",
                "size:S",
                "enhancement",
                "good first issue",
            ],
            body(
                "Diagnosis currently returns ad hoc strings; need a versioned schema.",
                "- Pydantic model for root-cause labels\n"
                "- Align case YAML `ground_truth.root_cause`",
                "- [ ] Schema in `runtime/schemas/`\n"
                "- [ ] Validator used by CaseRegistry",
            ),
        ),
        (
            "[M5] Supervised root-cause classifier baseline",
            "M5 — Diagnosis",
            ["type:runtime", "area:diagnosis", "priority:P1", "size:L", "enhancement"],
            body(
                "Learn mapping from trace features → root cause labels.",
                "- Train/eval split on labeled cases\n"
                "- sklearn pipeline behind `analysis` extra",
                "- [ ] Training script\n"
                "- [ ] Metrics reported\n"
                "- [ ] Deterministic toy fixture for CI",
            ),
        ),
        (
            "[M5] LLM-over-logs diagnosis baseline",
            "M5 — Diagnosis",
            ["type:runtime", "area:diagnosis", "priority:P2", "size:M", "enhancement"],
            body(
                "Compare LLM judging raw logs vs semantic traces (paired with next issue).",
                "- Provider-agnostic interface; mock in CI\n"
                "- Prompt + structured output schema",
                "- [ ] Baseline module\n"
                "- [ ] Mocked unit test",
            ),
        ),
        (
            "[M5] LLM-over-semantic-traces diagnosis baseline",
            "M5 — Diagnosis",
            ["type:runtime", "area:diagnosis", "priority:P2", "size:M", "enhancement"],
            body(
                "Hypothesis: semantic traces improve attribution vs raw logs.",
                "- Same interface as LLM-over-logs\n"
                "- Ablation hook for experiments",
                "- [ ] Baseline module\n"
                "- [ ] Mocked unit test",
            ),
        ),
        (
            "[M5] Counterfactual replay experiment harness",
            "M5 — Diagnosis",
            ["type:research", "area:diagnosis", "priority:P1", "size:L", "enhancement"],
            body(
                "Roadmap diagnosis caution: validate attributions via counterfactuals.",
                "- Replay episode with injector disabled/enabled\n"
                "- Measure outcome delta attributed to diagnosed cause",
                "- [ ] Harness CLI\n"
                "- [ ] One worked example on semantic-drift case",
            ),
        ),
        # ---- M6 ----
        (
            "[M6] Implement retry recovery policy",
            "M6 — Recovery",
            [
                "type:recovery",
                "priority:P1",
                "size:S",
                "enhancement",
                "good first issue",
            ],
            body(
                "Baseline recovery policy for comparison against failure-aware recovery.",
                "- Retry last action N times with budget\n"
                "- Evaluate on timeout/transient cases",
                "- [ ] Policy module\n"
                "- [ ] Tests",
            ),
        ),
        (
            "[M6] Implement restart recovery policy",
            "M6 — Recovery",
            ["type:recovery", "priority:P1", "size:S", "enhancement"],
            body(
                "Full task restart baseline.",
                "- Reset env + agent; re-run from step 0\n"
                "- Cost accounting for extra steps",
                "- [ ] Policy module\n"
                "- [ ] Tests",
            ),
        ),
        (
            "[M6] Implement refresh-context recovery policy",
            "M6 — Recovery",
            ["type:recovery", "priority:P1", "size:M", "enhancement"],
            body(
                "Needed for retrieval/memory staleness recoveries.",
                "- Clear/refetch context; replan pending actions\n"
                "- Wire into `suggest_recovery_actions` for retrieval/memory",
                "- [ ] Action + policy\n"
                "- [ ] Tests on a stale-retrieval or stale-memory case",
            ),
        ),
        (
            "[M6] Implement memory rollback recovery action",
            "M6 — Recovery",
            ["type:recovery", "priority:P0", "size:M", "enhancement"],
            body(
                "Paired with MemoryGuard vertical slice.",
                "- Roll back memory to last good checkpoint\n"
                "- Evaluate recovery success",
                "- [ ] Action implementation\n"
                "- [ ] Integration with stale/conflict memory cases",
            ),
        ),
        (
            "[M6] Human-escalation stub + safe abstain/stop policy",
            "M6 — Recovery",
            [
                "type:recovery",
                "priority:P1",
                "size:S",
                "enhancement",
                "good first issue",
            ],
            body(
                "High-risk paths should escalate or stop rather than silent retry.",
                "- Stub escalation event in traces\n"
                "- Stop/abstain action with risk gate",
                "- [ ] Stub + tests\n"
                "- [ ] Documented in `docs/recovery-policy.md`",
            ),
        ),
        (
            "[M6] Recovery evaluation harness (success, cost, safety)",
            "M6 — Recovery",
            ["type:recovery", "type:research", "priority:P0", "size:M", "enhancement"],
            body(
                "Compare policies on shared cases with common metrics.",
                "- Metrics: recovery success, extra steps/cost, irreversible side effects, escalations\n"
                "- Table output beside detector compare",
                "- [ ] Harness CLI\n"
                "- [ ] Results for semantic-drift + at least one other case",
            ),
        ),
        # ---- M7 ----
        (
            "[M7] Benchmark dataset card",
            "M7 — Research release v0.1",
            [
                "type:research",
                "area:docs",
                "documentation",
                "priority:P1",
                "size:M",
                "good first issue",
            ],
            body(
                "Required for research release and external adoption.",
                "- Dataset card covering tasks, failures, labels, licenses\n"
                "- Place under `datasets/cards/`",
                "- [ ] Card merged\n"
                "- [ ] Linked from README",
            ),
        ),
        (
            "[M7] Reproducibility guide",
            "M7 — Research release v0.1",
            ["type:research", "area:docs", "documentation", "priority:P1", "size:S"],
            body(
                "Pin how to reproduce tables from scratch.",
                "- Seeds, dependency pins, CLI commands\n"
                "- `docs/` guide + Makefile target",
                "- [ ] Guide published\n"
                "- [ ] Verified on clean checkout",
            ),
        ),
        (
            "[M7] Result tables + ablation study for first paper draft",
            "M7 — Research release v0.1",
            ["type:research", "priority:P0", "size:L", "enhancement"],
            body(
                "Core empirical artifact for Paper 1 (benchmark) / monitoring claims.",
                "- Tables for detection lead time, FPR, recovery success\n"
                "- Ablations: semantic features on/off",
                "- [ ] Checked-in results under `experiments/results/`\n"
                "- [ ] Short analysis note",
            ),
        ),
        (
            "[M7] Technical report scaffold filled with first results",
            "M7 — Research release v0.1",
            ["type:research", "area:docs", "documentation", "priority:P1", "size:L"],
            body(
                "`paper/main.tex` is a stub; expand with method + first tables.",
                "- Intro, method, experiments, limitations\n"
                "- Cite traces/results from repo",
                "- [ ] Compilable tex\n"
                "- [ ] PDF artifact optional in CI",
            ),
        ),
        (
            "[M7] Demonstration video / animated walkthrough",
            "M7 — Research release v0.1",
            ["type:research", "area:docs", "priority:P2", "size:M"],
            body(
                "Show semantic drift miss by exception monitors and recovery success.",
                "- Short screencast or generated animation\n"
                "- Link from README",
                "- [ ] Asset in `docs/assets/` or external link\n"
                "- [ ] README section",
            ),
        ),
        (
            "[M7] Project website (minimal)",
            "M7 — Research release v0.1",
            ["type:infra", "area:release", "priority:P2", "size:M", "enhancement"],
            body(
                "Roadmap includes website for adoption.",
                "- Static page from `website/` (GitHub Pages or similar)\n"
                "- Problem statement + quickstart + results teaser",
                "- [ ] Deployable site\n"
                "- [ ] Linked from README",
            ),
        ),
        (
            "[M7] Version 0.1.0 release (tag, CHANGELOG, PyPI optional)",
            "M7 — Research release v0.1",
            ["type:infra", "area:release", "priority:P0", "size:M"],
            body(
                "Ship first research release once suites + docs are ready.",
                "- CHANGELOG.md\n"
                "- GitHub Release + tag `v0.1.0`\n"
                "- Optional PyPI publish",
                "- [ ] Tag cut from main\n"
                "- [ ] Release notes summarize AgentFailBench slice + APIs",
            ),
        ),
        # Meta epic for next vertical slice
        (
            "[Epic] Next vertical slice: stale memory (MemoryGuard)",
            "M2 — Failure injection",
            [
                "type:benchmark",
                "type:research",
                "priority:P0",
                "size:L",
                "enhancement",
                "vertical-slice",
            ],
            body(
                "Roadmap §23 recommends vertical slices; tool semantic drift is done — memory is next.",
                "Coordinate across M2–M6:\n"
                "1. Inject stale memory\n"
                "2. Semantic traces for memory vs tool metadata\n"
                "3. Detector + diagnosis\n"
                "4. Memory rollback recovery\n"
                "5. Experiment report",
                "- [ ] Linked child issues completed\n"
                "- [ ] `experiments/results/stale-memory-001.md` published\n"
                "- [ ] README status updated",
            ),
        ),
    ]

    for title, ms, labels, b in open_issues:
        create_issue(title, ms, labels, b, close=False)

    print("\nSummary:")
    print(gh("issue", "list", "--repo", REPO, "--state", "open", "--limit", "50"))


if __name__ == "__main__":
    main()
