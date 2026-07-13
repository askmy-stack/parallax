"""Pydantic models for AgentFailBench case YAML."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TaskBlock(BaseModel):
    objective: str
    environment: str
    expected_steps: int = 8


class FailureBlock(BaseModel):
    category: str
    trigger_step: int
    visible_exception: bool = False
    reversible: bool = True


class GroundTruthBlock(BaseModel):
    root_cause: str
    first_detectable_step: int
    final_failure_step: int
    expected_recovery: list[str] = Field(default_factory=list)


class RiskBlock(BaseModel):
    severity: str = "medium"
    impact: str | None = None


class BenchmarkCaseModel(BaseModel):
    """Validated AgentFailBench case definition."""

    case_id: str
    task: TaskBlock
    failure: FailureBlock
    ground_truth: GroundTruthBlock
    risk: RiskBlock = Field(default_factory=RiskBlock)

    @property
    def failure_category(self) -> str:
        return self.failure.category

    def to_raw(self) -> dict[str, Any]:
        return self.model_dump()
