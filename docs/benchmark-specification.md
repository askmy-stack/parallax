# AgentFailBench Specification

## Objective

Evaluate the complete reliability lifecycle rather than final task success alone.

Each case should define controlled failure injection, semantic observability, ground-truth root cause, and expected recovery actions.

## Case schema (v0 draft)

```yaml
case_id: tool-semantic-drift-001

task:
  objective: update_customer_subscription
  environment: customer_service_api
  expected_steps: 8

failure:
  category: tool_semantic_drift
  trigger_step: 4
  visible_exception: false
  reversible: true

ground_truth:
  root_cause: plan_identifier_semantics_changed
  first_detectable_step: 5
  final_failure_step: 8
  expected_recovery:
    - refresh_tool_contract
    - validate_identifier_mapping
    - replan_pending_action

risk:
  severity: medium
  impact: incorrect_account_update
```

## Task families (initial)

1. Customer-support workflow
2. Database investigation
3. Cloud-resource inspection
4. Document retrieval and synthesis
5. File transformation
6. Data-quality investigation
7. Multi-step API workflow
8. Long-running memory task

## Failure suites (initial)

| Suite | Examples |
|---|---|
| ToolDrift | schema change, semantic change, permission change, latency shift, incomplete result, changed side effect |
| MemoryGuard | stale fact, conflicting memory, incorrect summary, irrelevant preference, poisoning, superseded state |
| Planning | repeated subgoal, incorrect ordering, premature completion, no-progress loop, failure to revise |
| Data & Retrieval | stale record, missing evidence, conflicting documents, altered distribution, delayed update |

## Version-one target

- 20–30 failure scenarios
- 5–8 task families
- 3 agent scaffolds
- 3 model providers or open models where feasible
- deterministic failure injection
- ground-truth root-cause and recovery labels
- reproducible configurations

## Package layout

```text
agentfailbench/
  tasks/
  environments/
  failures/
  labels/
  runners/
  registry.py
```
