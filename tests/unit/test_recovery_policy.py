"""Unit tests for recovery policy suggestions."""

from __future__ import annotations

from recovery.policies.suggest import suggest_recovery_actions
from runtime.schemas.taxonomy import FailureCategory, ToolFailureType


def test_tool_semantic_drift_recovery_order() -> None:
    actions = suggest_recovery_actions(
        FailureCategory.TOOL,
        ToolFailureType.SEMANTIC_DRIFT.value,
    )
    assert actions == [
        "refresh_tool_contract",
        "validate_identifier_mapping",
        "replan_pending_action",
    ]


def test_default_recovery_is_conservative() -> None:
    assert suggest_recovery_actions(FailureCategory.MODEL) == ["retry", "replan", "escalate"]
