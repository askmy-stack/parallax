"""Recovery action suggestion helpers.

Learning task: implement ``suggest_recovery_actions`` (see function docstring).
"""

from __future__ import annotations

from runtime.schemas.taxonomy import FailureCategory


def suggest_recovery_actions(
    category: FailureCategory,
    subtype: str | None = None,
) -> list[str]:
    """Return ordered recovery action names for a diagnosed failure.

    This function shapes RecoverAI's first policy table. Prefer specific,
    reversible actions before escalation or stop.

    Args:
        category: Top-level failure category from the taxonomy.
        subtype: Optional finer label (e.g. ``semantic_drift``).

    Returns:
        Ordered list of recovery action identifiers such as
        ``refresh_tool_contract``, ``retry``, ``replan``, ``rollback_memory``,
        ``escalate``, or ``stop``.

    Guidance:
        - For TOOL + semantic_drift, the first sprint expects:
          refresh_tool_contract → validate_identifier_mapping → replan_pending_action
        - Avoid recommending irreversible actions when the case is marked reversible
        - Prefer stop/escalate only when risk is high or recovery budget is exhausted
    """
    # --- YOUR IMPLEMENTATION (about 8–12 lines) ---
    # Map FailureCategory (+ optional subtype) to an ordered recovery plan.
    # Start with the tool semantic-drift vertical slice; other categories can
    # return a conservative default like ["retry", "replan", "escalate"].
    raise NotImplementedError("Implement suggest_recovery_actions — see docs/recovery-policy.md")
