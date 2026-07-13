"""Unit tests for package foundation."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from agentfailbench.registry import CaseRegistry
from runtime import __version__
from runtime.schemas import FailureCategory, TraceEvent
from runtime.schemas.trace import Expectation, Observation


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_failure_categories_cover_taxonomy() -> None:
    assert FailureCategory.TOOL.value == "tool"
    assert len(FailureCategory) == 10


def test_trace_event_expectation_observation_pair() -> None:
    event = TraceEvent(
        event_id="evt-1",
        timestamp=datetime.now(UTC),
        task_id="update_customer_subscription",
        scaffold="example-agent",
        entity="tool",
        name="get_subscription_plan",
        expectation=Expectation(attributes={"plan_id_meaning": "billing_plan_code"}),
        observation=Observation(success=True, attributes={"plan_id": "gold-annual"}),
    )
    assert event.has_expectation_observation_pair()


def test_load_tool_semantic_drift_case() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "agentfailbench"
        / "failures"
        / "tool_drift"
        / "tool-semantic-drift-001.yaml"
    )
    registry = CaseRegistry.from_yaml_file(path)
    assert registry.list_ids() == ["tool-semantic-drift-001"]
    case = registry.get("tool-semantic-drift-001")
    assert case.failure_category == "tool_semantic_drift"
    assert FailureCategory.TOOL in registry.categories_present()
