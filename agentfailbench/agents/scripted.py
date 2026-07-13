"""Deterministic scripted agents for AgentFailBench."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentfailbench.environments.customer_api.env import CustomerApiEnv, plan_id_meaning
from runtime.schemas.episode import Action


@dataclass
class ScriptedApiAgent:
    """Eight-step scripted tool sequence for update_customer_subscription."""

    env: CustomerApiEnv
    believed_meaning: str = "billing_plan_code"
    believed_plan_id: str | None = None
    history: list[dict[str, Any]] = field(default_factory=list)
    _step: int = 0

    def belief_plan_id(self) -> str:
        if self.believed_plan_id is not None:
            return self.believed_plan_id
        return self.env.task.target_plan_code

    def _sequence(self) -> list[Action]:
        customer_id = self.env.task.customer_id
        plan_id = self.belief_plan_id()
        return [
            Action(name="get_customer", arguments={"customer_id": customer_id}),
            Action(name="get_subscription", arguments={"customer_id": customer_id}),
            Action(name="get_plan", arguments={"plan_id": plan_id}),
            Action(name="get_subscription", arguments={"customer_id": customer_id}),
            Action(name="get_plan", arguments={"plan_id": plan_id}),
            Action(
                name="update_subscription",
                arguments={"customer_id": customer_id, "plan_id": plan_id},
            ),
            Action(name="get_subscription", arguments={"customer_id": customer_id}),
            Action(name="get_plan", arguments={"plan_id": plan_id}),
        ]

    def next_action(self) -> Action | None:
        sequence = self._sequence()
        if self._step >= len(sequence):
            return None
        action = sequence[self._step]
        action.step = self._step + 1
        self.history.append(
            {
                "step": action.step,
                "action": action.name,
                "expected_plan_id_meaning": self.believed_meaning,
                "expected_plan_id": self.belief_plan_id(),
            }
        )
        self._step += 1
        return action

    def expected_attributes(self) -> dict[str, Any]:
        return {
            "plan_id_meaning": self.believed_meaning,
            "plan_id": self.belief_plan_id(),
            "contract_belief": "v1" if self.believed_meaning == "billing_plan_code" else "v2",
        }

    def apply_contract_refresh(self, version: str = "v2") -> None:
        from typing import cast

        from agentfailbench.environments.customer_api.env import ContractVersion

        if version not in ("v1", "v2"):
            raise ValueError(f"unsupported contract version: {version}")
        cv = cast(ContractVersion, version)
        self.env.set_contract(cv)
        self.believed_meaning = plan_id_meaning(cv)
        self.believed_plan_id = self.env.true_plan_id_under_contract()
        self._step = 0

    def run_until_done(self, max_steps: int = 8) -> list[tuple[Action, Any]]:
        pairs: list[tuple[Action, Any]] = []
        for _ in range(max_steps):
            action = self.next_action()
            if action is None:
                break
            obs = self.env.step(action)
            pairs.append((action, obs))
        return pairs
