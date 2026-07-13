"""Integration test for the tool-semantic-drift vertical slice."""

from __future__ import annotations

from pathlib import Path

from agentfailbench.runners.episode import compare_detectors, run_episode


def test_clean_run_succeeds_without_false_alarm(tmp_path: Path) -> None:
    bundle = run_episode(
        "tool-semantic-drift-001",
        inject_failure=False,
        enable_recovery=False,
        export_dir=tmp_path,
    )
    assert bundle.result.success is True
    assert bundle.result.false_alarm is False
    semantic = next(r for r in bundle.detection_results if r.detector_name == "semantic_mismatch")
    assert semantic.detected is False


def test_drift_recover_compare(tmp_path: Path) -> None:
    failed = run_episode(
        "tool-semantic-drift-001",
        inject_failure=True,
        enable_recovery=False,
        export_dir=tmp_path,
    )
    assert failed.result.success is False
    assert failed.result.detected is True

    recovered = run_episode(
        "tool-semantic-drift-001",
        inject_failure=True,
        enable_recovery=True,
        export_dir=tmp_path,
    )
    assert recovered.result.recovery_success is True
    assert recovered.result.success is True
    assert recovered.result.diagnosed_cause == "plan_identifier_semantics_changed"

    report = compare_detectors("tool-semantic-drift-001", export_dir=tmp_path)
    by_name = {row["detector"]: row for row in report["detectors"]}
    assert by_name["semantic_mismatch"]["detected"] is True
    assert by_name["exception"]["detected"] is False
    assert report["recovery_success"] is True
    assert report["false_alarms_on_clean_run"]["semantic_mismatch"] is False
