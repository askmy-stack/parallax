"""Environment I/O and episode result contracts."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TaskSpec(BaseModel):
    """Specification for a benchmark task instance."""

    task_id: str
    objective: str
    environment: str
    customer_id: str = "cust_001"
    target_plan_code: str = "GOLD_ANNUAL"
    expected_steps: int = 8


class Action(BaseModel):
    """Agent action issued to an environment."""

    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    step: int = 0


class EnvObservation(BaseModel):
    """Environment response to an action (transport-level)."""

    success: bool
    status_code: int = 200
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    latency_ms: float = 1.0


class EpisodeResult(BaseModel):
    """Outcome of one monitored agent episode."""

    case_id: str
    success: bool
    steps: int
    detection_step: int | None = None
    detected: bool = False
    detector_name: str | None = None
    diagnosed_cause: str | None = None
    recovery_actions: list[str] = Field(default_factory=list)
    recovery_success: bool | None = None
    false_alarm: bool = False
    extra_steps: int = 0
    cost_units: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)
