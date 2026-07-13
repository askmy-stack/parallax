"""Recovery action suggestion helpers."""

from __future__ import annotations

from runtime.schemas.taxonomy import FailureCategory, ToolFailureType


def suggest_recovery_actions(
    category: FailureCategory,
    subtype: str | None = None,
) -> list[str]:
    """Return ordered recovery action names for a diagnosed failure."""
    normalized = (subtype or "").lower().replace("-", "_")
    if category is FailureCategory.TOOL and normalized in {
        ToolFailureType.SEMANTIC_DRIFT.value,
        "tool_semantic_drift",
        "semantic_tool_drift",
    }:
        return [
            "refresh_tool_contract",
            "validate_identifier_mapping",
            "replan_pending_action",
        ]
    if category is FailureCategory.MEMORY:
        return ["rollback_memory", "refresh_context", "replan", "escalate"]
    if category is FailureCategory.RETRIEVAL:
        return ["refresh_context", "replan", "escalate"]
    if category is FailureCategory.PLANNING:
        return ["replan", "restart", "escalate"]
    return ["retry", "replan", "escalate"]
