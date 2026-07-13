# ADR 0001: Repository layout and package boundaries

- **Status:** Accepted
- **Date:** 2026-07-13

## Context

The research roadmap defines four contributions (taxonomy, AgentFailBench, semantic monitoring, RecoverAI) that must evolve independently without becoming a single agent framework.

## Decision

Use top-level packages matching research modules:

- `agentfailbench/` — tasks, environments, injectors, labels, runners
- `runtime/` — tracing, schemas, features, detectors, diagnosis, calibration
- `recovery/` — policies, actions, constraints, sandbox, evaluation
- `baselines/` — comparison methods kept separate from proposed methods

Python packaging uses Hatchling with these packages as first-class installable modules (no `src/` layout) so imports match the research vocabulary in papers and docs.

## Consequences

- Clear mapping from papers → code directories
- Benchmark remains scaffold-agnostic
- Slightly less common than `src/` layout; documented here to avoid churn
