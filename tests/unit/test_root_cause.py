"""Unit tests for the versioned root-cause label schema."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from agentfailbench.registry import CaseRegistry
from runtime.schemas.root_cause import (
    ROOT_CAUSE_LABEL_SCHEMA_VERSION,
    RootCauseCode,
    RootCauseLabel,
    root_cause_label,
)
from runtime.schemas.taxonomy import FailureCategory

CASE_PATH = (
    Path(__file__).resolve().parents[2]
    / "agentfailbench"
    / "failures"
    / "tool_drift"
    / "tool-semantic-drift-001.yaml"
)


def test_root_cause_label_infers_category() -> None:
    label = root_cause_label(RootCauseCode.PLAN_IDENTIFIER_SEMANTICS_CHANGED)
    assert label.category == FailureCategory.TOOL
    assert label.schema_version == ROOT_CAUSE_LABEL_SCHEMA_VERSION


def test_root_cause_label_accepts_raw_string() -> None:
    label = root_cause_label("tool_transport_error")
    assert label.code is RootCauseCode.TOOL_TRANSPORT_ERROR
    assert label.category == FailureCategory.TOOL


def test_root_cause_label_rejects_mismatched_category() -> None:
    with pytest.raises(ValidationError):
        RootCauseLabel(
            code=RootCauseCode.PLAN_IDENTIFIER_SEMANTICS_CHANGED,
            category=FailureCategory.MEMORY,
        )


def test_root_cause_label_rejects_unknown_code() -> None:
    with pytest.raises(ValueError):
        root_cause_label("not_a_real_root_cause")


def test_case_registry_validates_root_cause_on_load() -> None:
    registry = CaseRegistry.from_yaml_file(CASE_PATH)
    case = registry.get("tool-semantic-drift-001")
    assert case.model.ground_truth.root_cause == RootCauseCode.PLAN_IDENTIFIER_SEMANTICS_CHANGED
    assert case.root_cause_label == root_cause_label(
        RootCauseCode.PLAN_IDENTIFIER_SEMANTICS_CHANGED
    )


def test_case_registry_rejects_unknown_root_cause(tmp_path: Path) -> None:
    bad_case = tmp_path / "bad-case.yaml"
    bad_case.write_text(
        """
case_id: bad-case-001
task:
  objective: update_customer_subscription
  environment: customer_service_api
  expected_steps: 8
failure:
  category: tool_semantic_drift
  trigger_step: 4
ground_truth:
  root_cause: not_a_real_root_cause
  first_detectable_step: 5
  final_failure_step: 8
""",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        CaseRegistry.from_yaml_file(bad_case)
