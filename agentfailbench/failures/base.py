"""Shared failure-injector interface for AgentFailBench suites.

Every failure-injection suite (tool drift, memory, planning, retrieval, data,
communication — see ``docs/roadmap.md`` Milestone 2) drives an episode through
the same three lifecycle hooks so a single dispatcher can coordinate
heterogeneous injectors without depending on their concrete types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from runtime.schemas.episode import EnvObservation


@runtime_checkable
class FailureInjector(Protocol):
    """Lifecycle contract every failure injector must implement.

    ``env`` is typed as ``Any`` on purpose: each suite injects failures into
    a different environment (customer API today, memory/retrieval stores in
    later milestones), so the interface stays environment-agnostic.
    """

    def before_step(self, env: Any, step: int) -> None:
        """Arm/apply the failure ahead of the upcoming step, if triggered."""
        ...

    def after_step(self, env: Any, step: int, observation: EnvObservation) -> None:
        """React to the outcome of a step that just executed."""
        ...

    def reset(self) -> None:
        """Return the injector to its pre-trigger state for a fresh episode."""
        ...

    @property
    def triggered(self) -> bool:
        """Whether the injected failure has fired at least once."""
        ...


@dataclass
class FailureInjectorRegistry:
    """Registers named injectors and dispatches lifecycle hooks to all of them."""

    _injectors: dict[str, FailureInjector] = field(default_factory=dict)

    def register(self, name: str, injector: FailureInjector) -> None:
        if name in self._injectors:
            raise ValueError(f"Duplicate failure injector: {name}")
        self._injectors[name] = injector

    def get(self, name: str) -> FailureInjector:
        return self._injectors[name]

    def list_names(self) -> list[str]:
        return sorted(self._injectors)

    def dispatch_before_step(self, env: Any, step: int) -> None:
        for injector in self._injectors.values():
            injector.before_step(env, step)

    def dispatch_after_step(self, env: Any, step: int, observation: EnvObservation) -> None:
        for injector in self._injectors.values():
            injector.after_step(env, step, observation)

    def dispatch_reset(self) -> None:
        for injector in self._injectors.values():
            injector.reset()

    def any_triggered(self) -> bool:
        return any(injector.triggered for injector in self._injectors.values())
