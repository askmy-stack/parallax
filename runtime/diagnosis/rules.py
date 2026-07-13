"""Rule-based root-cause diagnosis."""

from __future__ import annotations

from dataclasses import dataclass

from runtime.features.mismatch import semantic_mismatch
from runtime.schemas.taxonomy import FailureCategory, ToolFailureType
from runtime.schemas.trace import TraceEvent


@dataclass
class DiagnosisResult:
    category: FailureCategory
    subtype: str
    root_cause: str
    confidence: float


def diagnose_traces(events: list[TraceEvent]) -> DiagnosisResult | None:
    """Map semantic mismatch evidence to tool semantic drift root cause."""
    if any(semantic_mismatch(e) for e in events):
        return DiagnosisResult(
            category=FailureCategory.TOOL,
            subtype=ToolFailureType.SEMANTIC_DRIFT.value,
            root_cause="plan_identifier_semantics_changed",
            confidence=0.9,
        )
    for event in events:
        obs = event.observation
        if obs is not None and obs.success is False:
            return DiagnosisResult(
                category=FailureCategory.TOOL,
                subtype="transport_failure",
                root_cause="tool_transport_error",
                confidence=0.6,
            )
    return None
