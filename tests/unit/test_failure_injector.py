"""Unit tests for the shared failure-injector interface and registry."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from agentfailbench.environments.customer_api.env import CustomerApiEnv
from agentfailbench.failures.base import FailureInjector, FailureInjectorRegistry
from agentfailbench.failures.tool_drift.injector import (
    SemanticDriftInjector,
    SemanticDriftInjectorAdapter,
)
from runtime.schemas.episode import EnvObservation, TaskSpec


def _make_env() -> CustomerApiEnv:
    task = TaskSpec(
        task_id="t-1", objective="update_customer_subscription", environment="customer_service_api"
    )
    return CustomerApiEnv(task=task)


@dataclass
class _RecordingInjector:
    """Minimal stand-in suite used to exercise registration/dispatch in isolation."""

    calls: list[str] = field(default_factory=list)
    _triggered: bool = False

    def before_step(self, env: object, step: int) -> None:
        del env
        self.calls.append(f"before:{step}")
        self._triggered = True

    def after_step(self, env: object, step: int, observation: EnvObservation) -> None:
        del env, observation
        self.calls.append(f"after:{step}")

    def reset(self) -> None:
        self.calls.append("reset")
        self._triggered = False

    @property
    def triggered(self) -> bool:
        return self._triggered


def test_semantic_drift_adapter_satisfies_failure_injector_protocol() -> None:
    adapter = SemanticDriftInjectorAdapter(SemanticDriftInjector(trigger_step=2))
    assert isinstance(adapter, FailureInjector)


def test_recording_injector_satisfies_failure_injector_protocol() -> None:
    assert isinstance(_RecordingInjector(), FailureInjector)


def test_registry_rejects_duplicate_names() -> None:
    registry = FailureInjectorRegistry()
    registry.register("a", _RecordingInjector())
    with pytest.raises(ValueError):
        registry.register("a", _RecordingInjector())


def test_registry_get_and_list_names() -> None:
    registry = FailureInjectorRegistry()
    injector = _RecordingInjector()
    registry.register("only", injector)
    assert registry.list_names() == ["only"]
    assert registry.get("only") is injector


def test_registry_dispatches_lifecycle_hooks_to_all_injectors() -> None:
    registry = FailureInjectorRegistry()
    first = _RecordingInjector()
    second = _RecordingInjector()
    registry.register("first", first)
    registry.register("second", second)
    env = _make_env()
    obs = EnvObservation(success=True)

    registry.dispatch_before_step(env, 1)
    registry.dispatch_after_step(env, 1, obs)
    registry.dispatch_reset()

    assert first.calls == ["before:1", "after:1", "reset"]
    assert second.calls == ["before:1", "after:1", "reset"]


def test_registry_any_triggered_reflects_injector_state() -> None:
    registry = FailureInjectorRegistry()
    registry.register("only", _RecordingInjector())
    assert registry.any_triggered() is False
    registry.dispatch_before_step(_make_env(), 1)
    assert registry.any_triggered() is True


def test_adapter_delegates_to_wrapped_semantic_drift_injector() -> None:
    inner = SemanticDriftInjector(trigger_step=2)
    adapter = SemanticDriftInjectorAdapter(inner)
    env = _make_env()

    adapter.before_step(env, 1)
    assert adapter.triggered is False
    assert env.contract_version == "v1"

    adapter.before_step(env, 2)
    assert adapter.triggered is True
    assert env.contract_version == "v2"

    adapter.after_step(env, 2, EnvObservation(success=True))  # no-op, must not raise

    adapter.reset()
    assert adapter.triggered is False
    assert adapter.injector is inner
