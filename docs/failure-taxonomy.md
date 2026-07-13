# Agent Failure Taxonomy

Structured taxonomy of failures affecting autonomous agents **during valid task execution** (not only infrastructure crashes).

## Categories

### 9.1 Model failures

- hallucinated fact
- incorrect reasoning
- unsupported confidence
- instruction misunderstanding
- inability to abstain
- inconsistent answer across repeated runs

### 9.2 Planning failures

- invalid decomposition
- incorrect subgoal
- premature completion
- plan oscillation
- repeated loops
- excessive replanning
- failure to update the plan after new evidence

### 9.3 Memory failures

- stale memory
- conflicting memory
- duplicated memory
- irrelevant memory
- incorrect summarization
- poisoned memory
- missing provenance
- inappropriate memory influence

### 9.4 Retrieval failures

- stale document
- irrelevant retrieval
- incomplete context
- conflicting sources
- ranking failure
- missing current evidence
- overreliance on one source

### 9.5 Tool failures

- timeout
- schema drift
- semantic drift
- changed permissions
- incomplete response
- technically valid but wrong output
- changed side effects
- unexpected rate limits
- wrong parameter selection

### 9.6 Data failures

- missing fields
- corrupted values
- distribution shift
- delayed data
- duplicated data
- label inconsistency
- stale state

### 9.7 Environment failures

- external state changes
- changed task constraints
- resource unavailability
- new object or entity
- incompatible environment version
- action no longer valid

### 9.8 Communication failures

- dropped message
- delayed response
- duplicate message
- inconsistent agent-to-agent state
- misunderstood delegation
- loss of ordering

### 9.9 Execution failures

- action not performed
- partial action
- irreversible side effect
- expected state transition absent
- physical or simulated actuator delay
- mismatch between command and observed result

### 9.10 Recovery failures

- retry repeats the same failure
- recovery introduces a new failure
- rollback is incomplete
- escalation occurs too late
- unnecessary human intervention
- system continues despite high risk

## Implementation note

Machine-readable category enums live in `runtime/schemas/taxonomy.py`. Keep documentation and code enums synchronized when categories change.
