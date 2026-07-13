# Research Proposal

## Title

Reliable Agent Systems: Runtime Reliability, Diagnosis, and Recovery for Autonomous AI Agents

## Maintainer

Abhinaysai Kamineni

## Problem

Modern AI agents are evaluated mainly by final task success, static benchmarks, model confidence, tool exceptions, latency, or token usage. These signals miss many real failures: semantically wrong but valid API responses, stale memory, outdated retrieval, plan oscillation, and schema-preserving tool semantic drift.

### Central question

How can an autonomous AI system detect that it is becoming unreliable before visible task failure, distinguish the root cause of the degradation, estimate the risk of continuing, and select a safe and effective recovery strategy?

## Objectives

1. Develop a structured **runtime failure taxonomy** for autonomous agents.
2. Build **AgentFailBench** for controlled failure injection with ground-truth labels.
3. Design a **semantic runtime monitor** relating goals, beliefs, actions, expectations, observations, and state changes.
4. Evaluate **failure-aware recovery** (RecoverAI) against retry-only and generic self-reflection baselines.

## Scope

**Phase one:** digital tool-using agents (REST APIs, SQL, files, retrieval, memory, multi-step planning).

**Phase two:** one small simulated Physical AI environment for transfer validation (not advanced robotics).

**Out of scope for v0.1:** foundation-model training, universal agent frameworks, industrial robot deployment, unsupported formal safety claims.

## Hypotheses (summary)

- Semantic expected–observed signals detect failures earlier than exceptions or confidence alone.
- Root-cause-aware recovery outperforms retry/restart/generic reflection.
- Progress stagnation, repeated actions, state contradiction, and outcome mismatch transfer better across models than model-specific confidence.

## Method overview

```text
Agent execution → semantic traces → detection → diagnosis → risk → recovery → evaluation
```

Primary first vertical slice: **tool semantic drift** on a customer subscription update workflow.

## Evaluation dimensions

Task success, detection lead time, diagnosis accuracy, calibration, recovery success, cost, and safe abstention — not accuracy alone.

## Deliverables (first research release)

- Public benchmark + labels
- Trace schema + collectors
- Baseline detectors and recovery policies
- Reproducibility guide and technical report

## Related work (starting points)

- OpenTelemetry GenAI Semantic Conventions
- AI Agents That Matter / Princeton Science of Agent Evaluation
- τ-bench, AgentLAB, Memory-Induced Tool-Drift surveys and benchmarks

Full roadmap: [roadmap.md](roadmap.md).
