"""Episode runner for AgentFailBench vertical slices."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentfailbench.agents.scripted import ScriptedApiAgent
from agentfailbench.environments.customer_api.env import CustomerApiEnv
from agentfailbench.failures.base import FailureInjectorRegistry
from agentfailbench.failures.tool_drift.injector import (
    SemanticDriftInjector,
    SemanticDriftInjectorAdapter,
)
from agentfailbench.models import BenchmarkCaseModel
from agentfailbench.registry import CaseRegistry
from baselines.rules.detectors import BaseDetector, DetectionResult, all_detectors
from recovery.actions.tool_contract import apply_tool_contract_refresh
from runtime.diagnosis.rules import diagnose_traces
from runtime.schemas.episode import EpisodeResult, TaskSpec
from runtime.schemas.trace import TraceEvent
from runtime.tracing.collector import TraceCollector

CASES_ROOT = Path(__file__).resolve().parents[1] / "failures"


@dataclass
class EpisodeBundle:
    result: EpisodeResult
    detection_results: list[DetectionResult]
    traces_path: Path | None = None


def load_case(case_id: str) -> BenchmarkCaseModel:
    registry = CaseRegistry.from_directory(CASES_ROOT)
    return registry.get(case_id).model


def build_task(case: BenchmarkCaseModel) -> TaskSpec:
    return TaskSpec(
        task_id=case.case_id,
        objective=case.task.objective,
        environment=case.task.environment,
        expected_steps=case.task.expected_steps,
    )


def _run_traced(
    case: BenchmarkCaseModel,
    *,
    inject_failure: bool,
) -> tuple[CustomerApiEnv, ScriptedApiAgent, TraceCollector, SemanticDriftInjectorAdapter]:
    task = build_task(case)
    env = CustomerApiEnv(task=task)
    agent = ScriptedApiAgent(env=env)
    injector = SemanticDriftInjectorAdapter(
        SemanticDriftInjector(trigger_step=case.failure.trigger_step)
    )
    injectors = FailureInjectorRegistry()
    injectors.register("tool_drift.semantic_drift", injector)
    collector = TraceCollector(task_id=case.case_id)

    for _ in range(case.task.expected_steps):
        upcoming_step = agent._step + 1
        if inject_failure:
            injectors.dispatch_before_step(env, upcoming_step)
        action = agent.next_action()
        if action is None:
            break
        obs = env.step(action)
        if inject_failure:
            injectors.dispatch_after_step(env, upcoming_step, obs)
        progress = min(1.0, action.step / case.task.expected_steps)
        collector.record(action, obs, agent.expected_attributes(), progress)

    assert collector.validate_pairs()
    return env, agent, collector, injector


def run_episode(
    case_id: str = "tool-semantic-drift-001",
    *,
    inject_failure: bool = True,
    enable_recovery: bool = True,
    detector: BaseDetector | None = None,
    export_dir: Path | None = None,
) -> EpisodeBundle:
    """Run one episode for the customer-subscription semantic-drift case."""
    case = load_case(case_id)
    env, agent, collector, injector = _run_traced(case, inject_failure=inject_failure)

    traces_path: Path | None = None
    if export_dir is not None:
        export_dir.mkdir(parents=True, exist_ok=True)
        traces_path = export_dir / f"{case_id}.jsonl"
        collector.export_jsonl(traces_path)

    detection_results = [d.detect(collector.events) for d in all_detectors()]
    if detector is not None:
        primary = detector.detect(collector.events)
    else:
        primary = next(
            (r for r in detection_results if r.detector_name == "semantic_mismatch"),
            detection_results[0],
        )

    diagnosis = diagnose_traces(collector.events)
    recovery_actions: list[str] = []
    recovery_success: bool | None = None
    extra_steps = 0

    task_success = env.validate_success()
    if (
        enable_recovery
        and inject_failure
        and not task_success
        and diagnosis is not None
        and primary.detected
    ):
        outcome = apply_tool_contract_refresh(agent, diagnosis)
        recovery_actions = outcome.actions
        recovery_success = outcome.success
        extra_steps = outcome.extra_steps
        task_success = outcome.success

    false_alarm = bool(primary.detected and not inject_failure)

    result = EpisodeResult(
        case_id=case_id,
        success=task_success,
        steps=len(collector.events),
        detection_step=primary.detection_step,
        detected=primary.detected,
        detector_name=primary.detector_name,
        diagnosed_cause=diagnosis.root_cause if diagnosis else None,
        recovery_actions=recovery_actions,
        recovery_success=recovery_success,
        false_alarm=false_alarm,
        extra_steps=extra_steps,
        cost_units=float(len(collector.events) + extra_steps),
        metadata={
            "inject_failure": inject_failure,
            "injector_triggered": injector.triggered,
            "ground_truth_first_detectable": case.ground_truth.first_detectable_step,
            "ground_truth_root_cause": case.ground_truth.root_cause,
            "contract_final": env.contract_version,
        },
    )
    return EpisodeBundle(
        result=result, detection_results=detection_results, traces_path=traces_path
    )


def compare_detectors(
    case_id: str = "tool-semantic-drift-001",
    *,
    export_dir: Path | None = None,
) -> dict[str, Any]:
    """Run drifted episode once and evaluate all detectors on the same traces."""
    case = load_case(case_id)
    env, agent, collector, _injector = _run_traced(case, inject_failure=True)

    if export_dir is not None:
        export_dir.mkdir(parents=True, exist_ok=True)
        collector.export_jsonl(export_dir / f"{case_id}-compare.jsonl")

    rows: list[dict[str, Any]] = []
    diagnosis = diagnose_traces(collector.events)
    task_success_before = env.validate_success()

    for det in all_detectors():
        det_result = det.detect(collector.events)
        rows.append(
            {
                "detector": det.name,
                "detected": det_result.detected,
                "detection_step": det_result.detection_step,
                "reason": det_result.reason,
                "meets_first_detectable": (
                    det_result.detection_step is not None
                    and det_result.detection_step <= case.ground_truth.first_detectable_step
                )
                if det_result.detected
                else False,
            }
        )

    recovery_success = None
    recovery_actions: list[str] = []
    if not task_success_before and diagnosis is not None:
        outcome = apply_tool_contract_refresh(agent, diagnosis)
        recovery_success = outcome.success
        recovery_actions = outcome.actions

    clean_events = _collect_clean_events(case_id)
    false_alarms = {d.name: d.detect(clean_events).detected for d in all_detectors()}
    clean = run_episode(case_id, inject_failure=False, enable_recovery=False)

    return {
        "case_id": case_id,
        "task_success_before_recovery": task_success_before,
        "diagnosis": diagnosis.root_cause if diagnosis else None,
        "recovery_actions": recovery_actions,
        "recovery_success": recovery_success,
        "detectors": rows,
        "false_alarms_on_clean_run": false_alarms,
        "ground_truth": case.ground_truth.model_dump(),
        "clean_success": clean.result.success,
    }


def _collect_clean_events(case_id: str) -> list[TraceEvent]:
    case = load_case(case_id)
    _env, _agent, collector, _inj = _run_traced(case, inject_failure=False)
    return collector.events
