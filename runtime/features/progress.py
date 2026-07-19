"""Repeated-action and flat goal-progress features (planning-loop / stagnation signals)."""

from __future__ import annotations

from runtime.schemas.trace import TraceEvent


def _action_signature(event: TraceEvent) -> tuple[str, tuple[tuple[str, object], ...]]:
    """Identity of an action call: its name plus sorted arguments."""
    arguments = event.attributes.get("arguments", {})
    if not isinstance(arguments, dict):
        arguments = {}
    return event.name, tuple(sorted(arguments.items()))


def repeated_action_step(events: list[TraceEvent], min_repeats: int = 2) -> int | None:
    """Return the step of the first action repeated `min_repeats` times in a row.

    A "repeat" is a consecutive event with the same action name and arguments as the
    previous event — evidence the agent is stuck retrying the same move without
    revising its plan.
    """
    if min_repeats < 2:
        raise ValueError("min_repeats must be >= 2")
    streak = 1
    previous: tuple[str, tuple[tuple[str, object], ...]] | None = None
    for event in events:
        signature = _action_signature(event)
        streak = streak + 1 if signature == previous else 1
        previous = signature
        if streak >= min_repeats:
            step = event.attributes.get("step")
            return int(step) if step is not None else None
    return None


def flat_progress_step(events: list[TraceEvent], min_flat_steps: int = 3) -> int | None:
    """Return the step where goal progress has stalled for `min_flat_steps` events.

    Reads the `goal_progress` value recorded on each event's attributes by
    `TraceCollector`. Events without a recorded progress value are skipped rather
    than treated as stalled.
    """
    if min_flat_steps < 2:
        raise ValueError("min_flat_steps must be >= 2")
    streak = 1
    previous_progress: float | None = None
    for event in events:
        raw_progress = event.attributes.get("goal_progress")
        if raw_progress is None:
            continue
        progress = float(raw_progress)
        streak = (
            streak + 1 if previous_progress is not None and progress <= previous_progress else 1
        )
        previous_progress = progress
        if streak >= min_flat_steps:
            step = event.attributes.get("step")
            return int(step) if step is not None else None
    return None
