# Reliable Agent Systems

> **Reliable Agent Systems is an open-source research project for evaluating, detecting, diagnosing, and recovering from runtime failures in autonomous AI agents.**
>
> The project introduces AgentFailBench, a benchmark for controlled reliability degradation; a semantic trace model that captures goals, actions, expectations, observations, and state changes; and RecoverAI, a framework for evaluating failure-specific recovery strategies.
>
> The initial focus is tool-using digital agents, followed by multimodal and simulated Physical AI environments.

## Research identity

**Reliable and adaptive AI systems across digital and physical environments.**

This project studies how autonomous AI agents can continuously evaluate their own reliability, recognize when their assumptions are no longer valid, identify the likely source of failure, and choose a safe recovery strategy.

### Central problem

> How can an autonomous AI system detect that it is becoming unreliable before visible task failure, distinguish the root cause of the degradation, estimate the risk of continuing, and select a safe and effective recovery strategy?

## Core contributions

| Contribution | Module | Description |
|---|---|---|
| Runtime failure taxonomy | `docs/failure-taxonomy.md` | Structured failure classes during valid task execution |
| AgentFailBench | `agentfailbench/` | Controlled failure injection + ground-truth labels |
| Semantic Runtime Monitor | `runtime/` | Goals, beliefs, actions, expectations, observations |
| RecoverAI | `recovery/` | Failure-aware recovery policy evaluation |

## Reliability lifecycle

```text
Controlled failure
      ↓
Semantic execution trace
      ↓
Early failure detection
      ↓
Root-cause diagnosis
      ↓
Risk estimation
      ↓
Recovery selection
      ↓
Post-recovery evaluation
```

## Repository layout

```text
agentfailbench/   # Benchmark tasks, environments, failure injectors, labels
runtime/          # Tracing, schemas, features, detectors, diagnosis
recovery/         # Policies, actions, constraints, sandbox, evaluation
baselines/        # Rule, statistical, classical ML, sequence, LLM judges
experiments/      # Configs, scripts, notebooks, results
docs/             # Research specs and ADRs
examples/         # Minimal agent scaffolds
tests/            # Unit, integration, and benchmark tests
paper/            # Technical report / paper drafts
```

## Quick start

Requires **Python 3.12+**.

```bash
python -m venv .venv
source .venv/bin/activate
make install
make test
```

Optional local OpenTelemetry UI:

```bash
docker compose up -d jaeger
```

## Status

**Milestone 0 — Repository foundation** (in progress)

See [docs/roadmap.md](docs/roadmap.md) for the full research specification and [docs/research-proposal.md](docs/research-proposal.md) for the condensed proposal.

Immediate vertical slice: **tool semantic drift** in a customer-subscription update task (see sprint notes in the roadmap §30).

## Citation

See [CITATION.cff](CITATION.cff). Formal citation will be updated when a technical report or paper is released.

## License

MIT — see [LICENSE](LICENSE).

## Maintainer

Abhinaysai Kamineni ([askmy-stack](https://github.com/askmy-stack))
