"""Versioned root-cause label schema for AgentFailBench diagnosis output.

``runtime.diagnosis.rules`` and case-file ``ground_truth.root_cause`` values
previously used ad hoc free-text strings. This module gives those strings a
closed, versioned vocabulary (:class:`RootCauseCode`) plus a small
categorized wrapper (:class:`RootCauseLabel`) so new root causes are added
deliberately alongside their :class:`~runtime.schemas.taxonomy.FailureCategory`.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, model_validator

from runtime.schemas.taxonomy import FailureCategory

ROOT_CAUSE_LABEL_SCHEMA_VERSION = "1.0"


class RootCauseCode(StrEnum):
    """Known root-cause identifiers. Extend as new failure suites land."""

    PLAN_IDENTIFIER_SEMANTICS_CHANGED = "plan_identifier_semantics_changed"
    TOOL_TRANSPORT_ERROR = "tool_transport_error"


ROOT_CAUSE_CATEGORY: dict[RootCauseCode, FailureCategory] = {
    RootCauseCode.PLAN_IDENTIFIER_SEMANTICS_CHANGED: FailureCategory.TOOL,
    RootCauseCode.TOOL_TRANSPORT_ERROR: FailureCategory.TOOL,
}


class RootCauseLabel(BaseModel):
    """A root-cause code paired with its failure category and schema version."""

    code: RootCauseCode
    category: FailureCategory
    schema_version: str = ROOT_CAUSE_LABEL_SCHEMA_VERSION

    @model_validator(mode="after")
    def _category_matches_code(self) -> RootCauseLabel:
        expected = ROOT_CAUSE_CATEGORY.get(self.code)
        if expected is not None and self.category != expected:
            raise ValueError(
                f"root cause {self.code!r} belongs to category {expected!r}, got {self.category!r}"
            )
        return self


def root_cause_label(code: RootCauseCode | str) -> RootCauseLabel:
    """Build the :class:`RootCauseLabel` for ``code``, inferring its category.

    Raises ``ValueError`` (via enum/model validation) if ``code`` is not a
    recognized :class:`RootCauseCode`.
    """
    resolved = RootCauseCode(code)
    category = ROOT_CAUSE_CATEGORY.get(resolved)
    if category is None:
        raise ValueError(f"no category registered for root cause {resolved!r}")
    return RootCauseLabel(code=resolved, category=category)
