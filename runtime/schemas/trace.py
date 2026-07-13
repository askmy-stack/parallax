"""Core semantic trace models (OpenTelemetry-compatible attributes where practical)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from runtime.schemas.taxonomy import FailureCategory


class Expectation(BaseModel):
    """What the agent believed should happen for an action."""

    description: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class Observation(BaseModel):
    """What actually happened after an action."""

    description: str | None = None
    success: bool | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class TraceEvent(BaseModel):
    """One semantic execution event in an agent run."""

    event_id: str
    timestamp: datetime
    task_id: str
    scaffold: str
    entity: str
    name: str
    expectation: Expectation | None = None
    observation: Observation | None = None
    failure_category: FailureCategory | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)

    def has_expectation_observation_pair(self) -> bool:
        return self.expectation is not None and self.observation is not None
