"""Failure taxonomy enums aligned with docs/failure-taxonomy.md."""

from enum import StrEnum


class FailureCategory(StrEnum):
    """Top-level failure categories for AgentFailBench labels."""

    MODEL = "model"
    PLANNING = "planning"
    MEMORY = "memory"
    RETRIEVAL = "retrieval"
    TOOL = "tool"
    DATA = "data"
    ENVIRONMENT = "environment"
    COMMUNICATION = "communication"
    EXECUTION = "execution"
    RECOVERY = "recovery"


class ToolFailureType(StrEnum):
    """Tool-layer failure subtypes (ToolDrift suite)."""

    TIMEOUT = "timeout"
    SCHEMA_DRIFT = "schema_drift"
    SEMANTIC_DRIFT = "semantic_drift"
    PERMISSION_CHANGE = "permission_change"
    INCOMPLETE_RESPONSE = "incomplete_response"
    VALID_BUT_WRONG = "technically_valid_but_wrong"
    SIDE_EFFECT_CHANGE = "changed_side_effect"
    RATE_LIMIT = "unexpected_rate_limit"
    WRONG_PARAMETER = "wrong_parameter_selection"
