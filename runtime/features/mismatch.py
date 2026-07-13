"""Expected–observed mismatch features."""

from __future__ import annotations

from runtime.schemas.trace import TraceEvent


def semantic_mismatch(event: TraceEvent) -> bool:
    """True when plan_id_meaning (or contract belief) diverges."""
    if event.expectation is None or event.observation is None:
        return False
    exp = event.expectation.attributes
    obs = event.observation.attributes
    exp_meaning = exp.get("plan_id_meaning")
    obs_meaning = obs.get("plan_id_meaning")
    if exp_meaning is not None and obs_meaning is not None and exp_meaning != obs_meaning:
        return True
    exp_contract = exp.get("contract_belief")
    obs_contract = obs.get("contract_version")
    if exp_contract is not None and obs_contract is not None and exp_contract != obs_contract:
        return True
    return False


def first_mismatch_step(events: list[TraceEvent]) -> int | None:
    for event in events:
        if semantic_mismatch(event):
            step = event.attributes.get("step")
            return int(step) if step is not None else None
    return None
