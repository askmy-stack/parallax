# Contributing to Reliable Agent Systems

Thank you for contributing. This project is a research codebase: correctness, reproducibility, and clear evaluation matter more than feature volume.

## Ways to contribute

- **Benchmark cases** — new AgentFailBench tasks, environments, or failure injectors with ground-truth labels
- **Detectors / baselines** — detection or diagnosis methods with evaluation scripts
- **Recovery policies** — policies with measurable success/cost/safety metrics
- **Docs** — taxonomy refinements, ADRs, dataset cards, reproducibility notes
- **Bugs** — failing tests, incorrect labels, non-deterministic environments

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
make install
make ci
```

## Project conventions

1. **Python 3.12+** only.
2. Prefer **small, composable modules** over framework lock-in. AgentFailBench must stay usable across scaffolds.
3. Every failure case needs **ground-truth labels**: failure category, first detectable step, final failure step, expected recovery actions.
4. Prefer **deterministic environments** and fixed seeds for benchmark runs.
5. Do not claim formal safety guarantees. Frame results as empirical reliability evaluation.
6. Keep the first vertical slice focused: tool semantic drift before broad Physical AI work.

## Pull requests

1. Open an issue for non-trivial work when possible.
2. Keep PRs focused on one milestone concern (benchmark, tracing, detection, diagnosis, or recovery).
3. Include tests for new behavior.
4. Update docs when schemas, labels, or metrics change.
5. Run `make ci` before requesting review.

## Code style

- Format and lint with Ruff (`make format`, `make lint`)
- Type-check with mypy (`make typecheck`)
- Tests with pytest (`make test`)

## Conduct

Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

Do not open public issues for vulnerabilities. See [SECURITY.md](SECURITY.md).
