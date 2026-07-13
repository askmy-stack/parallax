"""Parallax CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime import __version__


def _cmd_version(_: argparse.Namespace) -> int:
    print(f"parallax {__version__}")
    return 0


def _cmd_experiment_run(args: argparse.Namespace) -> int:
    from agentfailbench.runners.episode import compare_detectors, run_episode

    export_dir = Path(args.export_dir)
    if args.compare:
        report = compare_detectors(args.case, export_dir=export_dir)
        out = export_dir / f"{args.case}-report.json"
        export_dir.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        _write_markdown_report(export_dir / f"{args.case}.md", report)
        print(json.dumps(report, indent=2))
        print(f"Wrote {out}")
        return 0

    bundle = run_episode(
        args.case,
        inject_failure=not args.clean,
        enable_recovery=not args.no_recovery,
        export_dir=export_dir,
    )
    print(bundle.result.model_dump_json(indent=2))
    return 0 if bundle.result.success or args.clean else 1


def _write_markdown_report(path: Path, report: dict[str, object]) -> None:
    detectors = report.get("detectors", [])
    assert isinstance(detectors, list)
    lines = [
        f"# Experiment: `{report['case_id']}`",
        "",
        "## Ground truth",
        "",
        "```json",
        json.dumps(report.get("ground_truth"), indent=2),
        "```",
        "",
        "## Detector comparison (drifted episode)",
        "",
        "| Detector | Detected | Step | Meets first_detectable | Reason |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in detectors:
        assert isinstance(row, dict)
        lines.append(
            f"| `{row['detector']}` | {row['detected']} | {row['detection_step']} | "
            f"{row['meets_first_detectable']} | {row['reason']} |"
        )
    lines.extend(
        [
            "",
            "## Outcomes",
            "",
            f"- Clean-run task success: **{report.get('clean_success')}**",
            f"- Drifted success before recovery: **{report.get('task_success_before_recovery')}**",
            f"- Diagnosis: `{report.get('diagnosis')}`",
            f"- Recovery actions: `{report.get('recovery_actions')}`",
            f"- Recovery success: **{report.get('recovery_success')}**",
            f"- False alarms on clean run: `{report.get('false_alarms_on_clean_run')}`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ras", description="Parallax reliability toolkit")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    sub = parser.add_subparsers(dest="command")

    exp = sub.add_parser("experiment", help="Run AgentFailBench experiments")
    exp_sub = exp.add_subparsers(dest="experiment_command")
    run = exp_sub.add_parser("run", help="Run a benchmark case")
    run.add_argument("--case", default="tool-semantic-drift-001")
    run.add_argument("--export-dir", default="experiments/results")
    run.add_argument("--compare", action="store_true", help="Compare all detectors + recovery")
    run.add_argument("--clean", action="store_true", help="Run without failure injection")
    run.add_argument("--no-recovery", action="store_true")
    run.set_defaults(func=_cmd_experiment_run)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version or args.command is None:
        raise SystemExit(_cmd_version(args))
    if args.command == "experiment":
        if getattr(args, "experiment_command", None) != "run":
            parser.parse_args(["experiment", "--help"])
            raise SystemExit(2)
        raise SystemExit(args.func(args))
    raise SystemExit(_cmd_version(args))


if __name__ == "__main__":
    main()
