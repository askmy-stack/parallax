# Recovery Policy (RecoverAI)

## Goal

Select recovery actions conditioned on diagnosed failure type, estimated risk, and reversibility — not only “retry until success.”

## Candidate actions

- retry
- replan
- refresh context / retrieval
- refresh tool contract
- switch tool or model
- roll back memory / state
- escalate to human
- stop / abstain
- sandbox and validate before commit

## Recovery state (minimum fields)

- diagnosed failure category
- confidence / calibration score
- reversibility
- remaining budget (time, tokens, cost)
- prior recovery attempts
- risk severity

## Baselines

- retry-only
- full task restart
- fixed rule table
- generic LLM self-reflection

## Objective

Maximize post-recovery task success and correctness while minimizing cost, latency, irreversible side effects, and unnecessary human escalation.

## First slice

For tool semantic drift:

1. detect expected–observed semantic mismatch
2. diagnose `tool_semantic_drift`
3. recover via **tool-contract refresh** + identifier remapping + replan of pending action
