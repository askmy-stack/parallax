"""Unit tests for detectors and diagnosis."""

from __future__ import annotations

from agentfailbench.runners.episode import _run_traced, load_case
from baselines.rules.detectors import (
    ConfidenceDetector,
    ExceptionDetector,
    RawTelemetryDetector,
    SemanticMismatchDetector,
)
from runtime.diagnosis.rules import diagnose_traces


def test_semantic_detector_catches_drift_exception_misses() -> None:
    case = load_case("tool-semantic-drift-001")
    _env, _agent, collector, injector = _run_traced(case, inject_failure=True)
    assert injector.triggered

    semantic = SemanticMismatchDetector().detect(collector.events)
    exception = ExceptionDetector().detect(collector.events)
    confidence = ConfidenceDetector().detect(collector.events)
    telemetry = RawTelemetryDetector().detect(collector.events)

    assert semantic.detected is True
    assert semantic.detection_step is not None
    assert semantic.detection_step <= case.ground_truth.first_detectable_step
    assert exception.detected is False
    assert confidence.detected is False
    assert telemetry.detected is False

    diagnosis = diagnose_traces(collector.events)
    assert diagnosis is not None
    assert diagnosis.root_cause == "plan_identifier_semantics_changed"
