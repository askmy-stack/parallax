"""Unit tests for the rule-based no-progress detector baseline."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from agentfailbench.runners.episode import _run_traced, load_case
from baselines.rules.detectors import NoProgressDetector, all_detectors
from runtime.schemas.trace import TraceEvent


def _event(
    name: str,
    step: int,
    *,
    arguments: dict[str, Any] | None = None,
    goal_progress: float | None = None,
) -> TraceEvent:
    return TraceEvent(
        event_id=f"evt-{step}",
        timestamp=datetime.now(UTC),
        task_id="test-task",
        scaffold="test-scaffold",
        entity="tool",
        name=name,
        attributes={
            "step": step,
            "arguments": arguments or {},
            "goal_progress": goal_progress,
        },
    )


def test_no_progress_detector_flags_repeated_action() -> None:
    events = [
        _event("get_customer", 1, arguments={"customer_id": "c1"}, goal_progress=0.2),
        _event("get_plan", 2, arguments={"plan_id": "p1"}, goal_progress=0.4),
        _event("get_plan", 3, arguments={"plan_id": "p1"}, goal_progress=0.5),
        _event("get_plan", 4, arguments={"plan_id": "p1"}, goal_progress=0.6),
    ]

    result = NoProgressDetector(min_repeats=2).detect(events)

    assert result.detected is True
    assert result.reason == "repeated_action"
    assert result.detection_step == 3


def test_no_progress_detector_flags_flat_goal_progress() -> None:
    events = [
        _event("get_customer", 1, arguments={"customer_id": "c1"}, goal_progress=0.2),
        _event("get_subscription", 2, arguments={"customer_id": "c1"}, goal_progress=0.4),
        _event("replan", 3, arguments={"attempt": 1}, goal_progress=0.4),
        _event("replan", 4, arguments={"attempt": 2}, goal_progress=0.4),
        _event("replan", 5, arguments={"attempt": 3}, goal_progress=0.3),
    ]

    result = NoProgressDetector(min_flat_steps=3).detect(events)

    assert result.detected is True
    assert result.reason == "flat_goal_progress"
    assert result.detection_step == 4


def test_no_progress_detector_ignores_non_consecutive_repeats() -> None:
    events = [
        _event("get_customer", 1, arguments={"customer_id": "c1"}, goal_progress=0.125),
        _event("get_subscription", 2, arguments={"customer_id": "c1"}, goal_progress=0.25),
        _event("get_plan", 3, arguments={"plan_id": "p1"}, goal_progress=0.375),
        _event("get_subscription", 4, arguments={"customer_id": "c1"}, goal_progress=0.5),
        _event("get_plan", 5, arguments={"plan_id": "p1"}, goal_progress=0.625),
        _event("update_subscription", 6, arguments={"plan_id": "p1"}, goal_progress=0.75),
        _event("get_subscription", 7, arguments={"customer_id": "c1"}, goal_progress=0.875),
        _event("get_plan", 8, arguments={"plan_id": "p1"}, goal_progress=1.0),
    ]

    result = NoProgressDetector().detect(events)

    assert result.detected is False
    assert result.reason == "progress_nominal"


def test_no_progress_detector_is_registered_in_all_detectors() -> None:
    names = [detector.name for detector in all_detectors()]
    assert "no_progress" in names


def test_no_progress_detector_no_false_alarm_on_clean_scripted_episode() -> None:
    case = load_case("tool-semantic-drift-001")
    _env, _agent, collector, _injector = _run_traced(case, inject_failure=False)

    result = NoProgressDetector().detect(collector.events)

    assert result.detected is False


def test_no_progress_detector_no_false_alarm_on_drifted_scripted_episode() -> None:
    case = load_case("tool-semantic-drift-001")
    _env, _agent, collector, injector = _run_traced(case, inject_failure=True)
    assert injector.triggered

    result = NoProgressDetector().detect(collector.events)

    assert result.detected is False
