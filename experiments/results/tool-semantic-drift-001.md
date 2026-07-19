# Experiment: `tool-semantic-drift-001`

## Ground truth

```json
{
  "root_cause": "plan_identifier_semantics_changed",
  "first_detectable_step": 5,
  "final_failure_step": 8,
  "expected_recovery": [
    "refresh_tool_contract",
    "validate_identifier_mapping",
    "replan_pending_action"
  ]
}
```

## Detector comparison (drifted episode)

| Detector | Detected | Step | Meets first_detectable | Reason |
| --- | --- | --- | --- | --- |
| `exception` | False | None | False | no_exceptions |
| `confidence` | False | None | False | confidence_unavailable_in_scripted_scaffold |
| `raw_telemetry` | False | None | False | telemetry_nominal |
| `semantic_mismatch` | True | 4 | True | plan_id_meaning_or_contract_divergence |
| `no_progress` | False | None | False | progress_nominal |

## Outcomes

- Clean-run task success: **True**
- Drifted success before recovery: **False**
- Diagnosis: `plan_identifier_semantics_changed`
- Recovery actions: `['refresh_tool_contract', 'validate_identifier_mapping', 'replan_pending_action']`
- Recovery success: **True**
- False alarms on clean run: `{'exception': False, 'confidence': False, 'raw_telemetry': False, 'semantic_mismatch': False, 'no_progress': False}`
