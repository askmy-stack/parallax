"""Detection baselines for reliability monitoring."""

from __future__ import annotations

from dataclasses import dataclass

from runtime.features.mismatch import first_mismatch_step, semantic_mismatch
from runtime.schemas.trace import TraceEvent


@dataclass
class DetectionResult:
    detector_name: str
    detected: bool
    detection_step: int | None = None
    false_alarm: bool = False
    reason: str = ""


class BaseDetector:
    name: str = "base"

    def detect(self, events: list[TraceEvent]) -> DetectionResult:
        raise NotImplementedError


class ExceptionDetector(BaseDetector):
    """Flags only explicit transport failures (non-2xx / success=False)."""

    name = "exception"

    def detect(self, events: list[TraceEvent]) -> DetectionResult:
        for event in events:
            obs = event.observation
            if obs is None:
                continue
            status = obs.attributes.get("status_code", 200)
            if obs.success is False or (isinstance(status, int) and status >= 400):
                step = event.attributes.get("step")
                return DetectionResult(
                    detector_name=self.name,
                    detected=True,
                    detection_step=int(step) if step is not None else None,
                    reason="transport_or_exception_failure",
                )
        return DetectionResult(detector_name=self.name, detected=False, reason="no_exceptions")


class ConfidenceDetector(BaseDetector):
    """Stub: model confidence is absent in scripted runs — never detects."""

    name = "confidence"

    def detect(self, events: list[TraceEvent]) -> DetectionResult:
        _ = events
        return DetectionResult(
            detector_name=self.name,
            detected=False,
            reason="confidence_unavailable_in_scripted_scaffold",
        )


class RawTelemetryDetector(BaseDetector):
    """Flags retry bursts or latency spikes only (no semantic awareness)."""

    name = "raw_telemetry"

    def detect(self, events: list[TraceEvent]) -> DetectionResult:
        retries = 0
        for event in events:
            obs = event.observation
            if obs is None:
                continue
            latency = float(obs.attributes.get("latency_ms", 0))
            if latency > 500:
                step = event.attributes.get("step")
                return DetectionResult(
                    detector_name=self.name,
                    detected=True,
                    detection_step=int(step) if step is not None else None,
                    reason="latency_spike",
                )
            if obs.success is False:
                retries += 1
                if retries >= 3:
                    step = event.attributes.get("step")
                    return DetectionResult(
                        detector_name=self.name,
                        detected=True,
                        detection_step=int(step) if step is not None else None,
                        reason="retry_burst",
                    )
        return DetectionResult(detector_name=self.name, detected=False, reason="telemetry_nominal")


class SemanticMismatchDetector(BaseDetector):
    """Detects expected vs observed plan_id_meaning / contract divergence."""

    name = "semantic_mismatch"

    def detect(self, events: list[TraceEvent]) -> DetectionResult:
        step = first_mismatch_step(events)
        if step is None:
            return DetectionResult(detector_name=self.name, detected=False, reason="aligned")
        # Confirm at least one mismatch event exists
        assert any(semantic_mismatch(e) for e in events)
        return DetectionResult(
            detector_name=self.name,
            detected=True,
            detection_step=step,
            reason="plan_id_meaning_or_contract_divergence",
        )


def all_detectors() -> list[BaseDetector]:
    return [
        ExceptionDetector(),
        ConfidenceDetector(),
        RawTelemetryDetector(),
        SemanticMismatchDetector(),
    ]
