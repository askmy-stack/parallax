"""Tool semantic-drift failure injector."""

from __future__ import annotations

from dataclasses import dataclass

from agentfailbench.environments.customer_api.env import CustomerApiEnv


@dataclass
class SemanticDriftInjector:
    """Flip tool contract v1→v2 at a configured trigger step (no exceptions)."""

    trigger_step: int = 4
    _armed: bool = True
    _triggered: bool = False

    def before_step(self, env: CustomerApiEnv, step: int) -> None:
        """Apply drift when the upcoming step reaches the trigger."""
        if self._armed and not self._triggered and step >= self.trigger_step:
            env.set_contract("v2")
            self._triggered = True

    @property
    def triggered(self) -> bool:
        return self._triggered

    def reset(self) -> None:
        self._triggered = False
