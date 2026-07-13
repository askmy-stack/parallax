<p align="center">
  <img src="docs/assets/hero-banner.jpg" alt="Parallax — Reliable Agent Systems: Detect, Diagnose, Recover" width="920" />
</p>

<h1 align="center">Parallax</h1>

<p align="center">
  <strong>When expectation and observation diverge, reliability is already failing.</strong>
</p>

<p align="center">
  Runtime reliability, diagnosis, and recovery for autonomous AI agents.<br/>
  Research stack: <em>AgentFailBench</em> · <em>Semantic Runtime Monitor</em> · <em>RecoverAI</em>
</p>

<p align="center">
  <a href="https://github.com/askmy-stack/parallax/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/askmy-stack/parallax/actions/workflows/ci.yml/badge.svg" /></a>
  <a href="https://www.python.org/downloads/"><img alt="Python 3.12+" src="https://img.shields.io/badge/python-3.12%2B-0d9488?logo=python&logoColor=white" /></a>
  <a href="LICENSE"><img alt="License MIT" src="https://img.shields.io/badge/license-MIT-1f2933" /></a>
  <a href="docs/research-proposal.md"><img alt="Research" src="https://img.shields.io/badge/status-research%20scaffold-f59e0b" /></a>
  <a href="docs/roadmap.md"><img alt="Milestone 0" src="https://img.shields.io/badge/milestone-0%20foundation-14b8a6" /></a>
</p>

---

## Why Parallax?

In optics, **parallax** is the apparent shift of an object when viewed from two positions.

In agent systems, the same failure mode appears as a gap between:

| Viewpoint | Signal |
| --- | --- |
| **Expectation** | What the agent believed a tool, memory, or plan step meant |
| **Observation** | What the environment actually returned |

If those viewpoints drift while HTTP still returns `200`, classic monitors stay quiet — and the task fails later, with the diagnostic window already closed.

<p align="center">
  <img src="docs/assets/semantic-drift.gif" alt="Animated expected vs observed path divergence (semantic drift)" width="720" />
</p>

<p align="center">
  <em>Parallax measures that gap early — then diagnoses and recovers.</em>
</p>

### Central question

> How can an autonomous system detect that it is becoming unreliable **before** visible task failure, distinguish the root cause, estimate the risk of continuing, and choose a safe recovery strategy?

---

## The invisible failure

<p align="center">
  <img src="docs/assets/semantic-mismatch.jpg" alt="Expectation vs observation: tool semantic drift with HTTP 200" width="920" />
</p>

**Tool semantic drift** is the first vertical slice: schema stays valid, transport succeeds, meaning changes. The agent acts on the wrong world model — and nothing throws.

AgentFailBench injects that class of failure with ground-truth labels so detectors and recovery policies can be evaluated, not just demoed.

---

## Reliability lifecycle

<p align="center">
  <img src="docs/assets/reliability-lifecycle.gif" alt="Animated reliability lifecycle from failure injection through recovery evaluation" width="920" />
</p>

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

---

## Reliability stack

<p align="center">
  <img src="docs/assets/architecture-overview.jpg" alt="Reliability stack: execution, semantic traces, intelligence, recovery, evaluation" width="860" />
</p>

| Layer | Package | Role |
| --- | --- | --- |
| Benchmark | `agentfailbench/` | Tasks, environments, injectors, ground-truth labels |
| Monitor | `runtime/` | Traces, features, detectors, diagnosis, calibration |
| Recovery | `recovery/` | Policies, actions, constraints, sandbox evaluation |
| Baselines | `baselines/` | Rules, classical ML, sequence models, LLM judges |

```mermaid
flowchart TB
  A[Agent task] --> B[Execution layer]
  B --> C[Semantic Trace Collector]
  C --> D[Reliability Intelligence]
  D --> E[Recovery Governor]
  E --> F[Evaluation Layer]
  F -.->|metrics| D
```

---

## Core contributions

| # | Contribution | What you get |
| --- | --- | --- |
| 1 | **Failure taxonomy** | Model · planning · memory · retrieval · tool · data · environment · communication · execution · recovery |
| 2 | **AgentFailBench** | Controlled degradation with first-detectable / final-failure steps |
| 3 | **Semantic Runtime Monitor** | Goals, beliefs, actions, expectations, observations, state changes |
| 4 | **RecoverAI** | Failure-conditioned recovery vs retry-only / restart / generic reflection |

---

## Quick start

Requires **Python 3.12+**.

```bash
git clone https://github.com/askmy-stack/parallax.git
cd parallax

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

make install
make test
ras                  # prints package version
```

Optional local telemetry UI:

```bash
docker compose up -d jaeger
# UI → http://localhost:16686
```

Inspect the first benchmark case:

```bash
cat agentfailbench/failures/tool_drift/tool-semantic-drift-001.yaml
```

---

## Repository map

```text
parallax/
├── agentfailbench/     # benchmark cases + injectors
├── runtime/            # semantic monitor + detectors
├── recovery/           # RecoverAI policies
├── baselines/          # comparison methods
├── experiments/        # configs · notebooks · results
├── docs/               # specs · ADRs · roadmap
│   └── assets/         # README visuals
├── examples/           # minimal agent scaffolds
├── tests/              # unit · integration · benchmark
└── paper/              # technical report scaffold
```

---

## Research status

| Milestone | Focus | Status |
| --- | --- | --- |
| **0** | Repository foundation | ✅ scaffolded |
| **1** | Minimal agent environments | next |
| **2** | Failure injection suite | planned |
| **3** | Semantic tracing | planned |
| **4–6** | Detection · diagnosis · recovery | planned |
| **7** | Research release v0.1 | planned |

Full specification: [`docs/roadmap.md`](docs/roadmap.md)  
Condensed proposal: [`docs/research-proposal.md`](docs/research-proposal.md)  
Taxonomy: [`docs/failure-taxonomy.md`](docs/failure-taxonomy.md)

**Near-term experiment:** compare exception monitoring, confidence thresholds, raw telemetry anomaly detection, and semantic expected–observed monitoring on tool semantic drift.

---

## Design principles

1. **Benchmark before framework** — AgentFailBench stays scaffold-agnostic.
2. **Semantics over status codes** — expectations and observations are first-class.
3. **Label everything** — detection lead time and root cause need ground truth.
4. **Recovery is a policy** — not an infinite retry loop.
5. **No false safety claims** — empirical reliability evaluation, not formal guarantees.

---

## Contributing

Research contributions welcome: new failure cases, detectors, recovery policies, and ablation studies.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

Security reports: [`SECURITY.md`](SECURITY.md).

---

## Citation

```bibtex
@software{parallax2026,
  author  = {Kamineni, Abhinaysai},
  title   = {Parallax: Reliable Agent Systems},
  year    = {2026},
  url     = {https://github.com/askmy-stack/parallax},
  version = {0.1.0}
}
```

Also see [`CITATION.cff`](CITATION.cff).

---

## License

MIT — see [`LICENSE`](LICENSE).

<p align="center">
  <sub>
    Capable agents must not only know how to act.<br/>
    They must recognize when their assumptions are failing — and choose when to retry, adapt, ask for help, or stop.
  </sub>
</p>
