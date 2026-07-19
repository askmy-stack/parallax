"""Semantic trace collector."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from runtime.schemas.episode import Action, EnvObservation
from runtime.schemas.trace import Expectation, Observation, TraceEvent


class TraceCollector:
    """Collect expectation–observation pairs for an episode."""

    def __init__(self, task_id: str, scaffold: str = "scripted-api-agent") -> None:
        self.task_id = task_id
        self.scaffold = scaffold
        self.events: list[TraceEvent] = []
        self.goal_progress: list[float] = []

    def record(
        self,
        action: Action,
        observation: EnvObservation,
        expectation_attrs: dict[str, Any],
        goal_progress: float,
    ) -> TraceEvent:
        obs_attrs: dict[str, Any] = {
            "status_code": observation.status_code,
            "latency_ms": observation.latency_ms,
            **observation.data,
        }
        if observation.error:
            obs_attrs["error"] = observation.error

        event = TraceEvent(
            event_id=str(uuid4()),
            timestamp=datetime.now(UTC),
            task_id=self.task_id,
            scaffold=self.scaffold,
            entity="tool",
            name=action.name,
            expectation=Expectation(
                description=f"Agent belief for {action.name}",
                attributes=dict(expectation_attrs),
            ),
            observation=Observation(
                description=f"Environment result for {action.name}",
                success=observation.success,
                attributes=obs_attrs,
            ),
            attributes={
                "step": action.step,
                "arguments": action.arguments,
                "goal_progress": goal_progress,
            },
        )
        self.events.append(event)
        self.goal_progress.append(goal_progress)
        return event

    def validate_pairs(self) -> bool:
        return all(e.has_expectation_observation_pair() for e in self.events)

    def export_jsonl(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            for event in self.events:
                fh.write(event.model_dump_json() + "\n")

    def to_serializable(self) -> list[dict[str, Any]]:
        return [json.loads(e.model_dump_json()) for e in self.events]
