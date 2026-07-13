"""Tool-contract refresh recovery action."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentfailbench.agents.scripted import ScriptedApiAgent
from recovery.policies.suggest import suggest_recovery_actions
from runtime.diagnosis.rules import DiagnosisResult
from runtime.schemas.episode import Action, EnvObservation


@dataclass
class RecoveryOutcome:
    actions: list[str]
    success: bool
    extra_steps: int
    details: dict[str, Any]


def apply_tool_contract_refresh(
    agent: ScriptedApiAgent,
    diagnosis: DiagnosisResult,
    target_version: str = "v2",
) -> RecoveryOutcome:
    """Refresh contract beliefs, remap plan id, and re-run the scripted plan."""
    actions = suggest_recovery_actions(diagnosis.category, diagnosis.subtype)
    refresh = Action(
        name="refresh_tool_contract",
        arguments={"version": target_version},
        step=0,
    )
    obs: EnvObservation = agent.env.step(refresh)
    if not obs.success:
        return RecoveryOutcome(
            actions=actions,
            success=False,
            extra_steps=1,
            details={"error": obs.error},
        )

    agent.apply_contract_refresh(target_version)
    pairs = agent.run_until_done(max_steps=8)
    extra = 1 + len(pairs)
    success = agent.env.validate_success()
    return RecoveryOutcome(
        actions=actions,
        success=success,
        extra_steps=extra,
        details={
            "contract_version": target_version,
            "plan_id_used": agent.belief_plan_id(),
            "replay_steps": len(pairs),
        },
    )
