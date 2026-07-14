"""Tool semantic-drift failure injector."""

from __future__ import annotations

from dataclasses import dataclass, field

from agentfailbench.environments.customer_api.env import CustomerApiEnv
from runtime.schemas.episode import EnvObservation


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


@dataclass
class SemanticDriftInjectorAdapter:
    """Adapts :class:`SemanticDriftInjector` to the shared ``FailureInjector`` protocol.

    ``SemanticDriftInjector`` predates the shared interface (``agentfailbench.failures.base``)
    and only needs a trigger-based ``before_step``/``reset``. This adapter fills in the
    ``after_step`` hook so the injector can be registered and dispatched alongside future
    suites without changing its existing behavior.
    """

    injector: SemanticDriftInjector = field(default_factory=SemanticDriftInjector)

    def before_step(self, env: CustomerApiEnv, step: int) -> None:
        self.injector.before_step(env, step)

    def after_step(self, env: CustomerApiEnv, step: int, observation: EnvObservation) -> None:
        """No-op: semantic drift is a one-shot contract flip with no post-step reaction."""
        del env, step, observation

    def reset(self) -> None:
        self.injector.reset()

    @property
    def triggered(self) -> bool:
        return self.injector.triggered
