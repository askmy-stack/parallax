# Experimental Protocol

## Guiding principle

Measure the reliability lifecycle end-to-end: observability → early detection → attribution → recovery → post-recovery outcomes.

## Primary experiment families

1. **Failure observability** — which failures are invisible to exception/confidence monitors?
2. **Early detection** — lead time before final task failure
3. **Semantic ablation** — contribution of expectation–observation features
4. **Root-cause attribution** — diagnosis accuracy vs. baselines
5. **Recovery policy** — success, cost, safety vs. retry/restart/reflection
6. **Cross-model / cross-scaffold** — transfer of detectors and policies
7. **Cost-aware evaluation** — dollars, tokens, latency vs. reliability gains
8. **Physical AI transfer** — small simulated environment validation

## First vertical-slice experiment

**Failure:** tool semantic drift (plan identifier meaning changes; HTTP 200).

**Compare:**

1. explicit exception monitoring
2. model-confidence monitoring
3. raw telemetry anomaly detection
4. semantic expected–observed monitoring

**Metrics:** detection yes/no, detection step, false alarms, final task success, recovery success, additional cost.

## Reproducibility requirements

- fixed seeds
- versioned case YAML
- pinned dependency sets for reported tables
- export traces to Parquet
- record model/scaffold/tool-contract versions
