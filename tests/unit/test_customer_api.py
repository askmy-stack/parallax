"""Unit tests for customer API environment and injector."""

from __future__ import annotations

from agentfailbench.agents.scripted import ScriptedApiAgent
from agentfailbench.environments.customer_api.env import CustomerApiEnv
from agentfailbench.failures.tool_drift.injector import SemanticDriftInjector
from runtime.schemas.episode import Action, TaskSpec


def test_clean_episode_succeeds() -> None:
    task = TaskSpec(
        task_id="t1",
        objective="update_customer_subscription",
        environment="customer_service_api",
    )
    env = CustomerApiEnv(task=task)
    agent = ScriptedApiAgent(env=env)
    agent.run_until_done()
    assert env.validate_success()


def test_semantic_drift_causes_wrong_update() -> None:
    task = TaskSpec(
        task_id="t1",
        objective="update_customer_subscription",
        environment="customer_service_api",
    )
    env = CustomerApiEnv(task=task)
    agent = ScriptedApiAgent(env=env)
    injector = SemanticDriftInjector(trigger_step=4)
    for _ in range(8):
        upcoming = agent._step + 1
        injector.before_step(env, upcoming)
        action = agent.next_action()
        if action is None:
            break
        env.step(action)
    assert injector.triggered
    assert not env.validate_success()


def test_contract_refresh_recovery() -> None:
    task = TaskSpec(
        task_id="t1",
        objective="update_customer_subscription",
        environment="customer_service_api",
    )
    env = CustomerApiEnv(task=task)
    # Simulate wrong v2 update
    env.set_contract("v2")
    env.step(
        Action(
            name="update_subscription",
            arguments={"customer_id": task.customer_id, "plan_id": "GOLD_ANNUAL"},
            step=1,
        )
    )
    assert not env.validate_success()
    agent = ScriptedApiAgent(env=env)
    agent.apply_contract_refresh("v2")
    agent.run_until_done()
    assert env.validate_success()
