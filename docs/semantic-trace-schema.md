# Semantic Trace Schema

Extend OpenTelemetry GenAI conventions with research-specific semantic attributes. Prefer compatibility with OTLP exporters; do not invent a parallel telemetry stack when standards apply.

## Core entities

- `task`
- `goal`
- `plan`
- `subgoal`
- `belief`
- `memory`
- `retrieval`
- `tool`
- `action`
- `observation`
- `state`
- `expectation`
- `error`
- `retry`
- `recovery`
- `human_intervention`
- `risk`

## Design principles

1. Every action should record **expected outcome** and **observed outcome**.
2. Goal progress should be measurable (stagnation / oscillation detectable).
3. Memory and retrieval events need provenance and freshness metadata.
4. Tool calls need contract version / semantic identity, not only schema hash.
5. Recovery attempts are first-class events, not afterthought logs.

## Example event (illustrative YAML)

```yaml
event_id: evt-0042
timestamp: 2026-07-13T20:00:00Z
task_id: update_customer_subscription
scaffold: example-agent
entity: tool
name: get_subscription_plan
attributes:
  expectation:
    plan_id_meaning: billing_plan_code
  observation:
    plan_id: "gold-annual"
    http_status: 200
  mismatch:
    type: semantic_identity
    field: plan_id
    severity: medium
```

## Implementation

Pydantic models live under `runtime/schemas/`. Collectors live under `runtime/tracing/`.
