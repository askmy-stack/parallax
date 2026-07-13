"""Registry for AgentFailBench cases."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from runtime.schemas.taxonomy import FailureCategory


@dataclass
class BenchmarkCase:
    """Parsed AgentFailBench case definition."""

    case_id: str
    raw: dict[str, Any]

    @property
    def failure_category(self) -> str | None:
        failure = self.raw.get("failure", {})
        if isinstance(failure, dict):
            value = failure.get("category")
            return str(value) if value is not None else None
        return None


@dataclass
class CaseRegistry:
    """In-memory registry of benchmark cases loaded from YAML."""

    cases: dict[str, BenchmarkCase] = field(default_factory=dict)

    def register(self, case: BenchmarkCase) -> None:
        if case.case_id in self.cases:
            raise ValueError(f"Duplicate case_id: {case.case_id}")
        self.cases[case.case_id] = case

    def get(self, case_id: str) -> BenchmarkCase:
        return self.cases[case_id]

    def list_ids(self) -> list[str]:
        return sorted(self.cases)

    @classmethod
    def from_yaml_file(cls, path: Path) -> CaseRegistry:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Case file must be a mapping: {path}")
        case_id = data.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"Missing case_id in {path}")
        registry = cls()
        registry.register(BenchmarkCase(case_id=case_id, raw=data))
        return registry

    def categories_present(self) -> set[FailureCategory]:
        """Return FailureCategory values present in registered cases when parseable."""
        found: set[FailureCategory] = set()
        for case in self.cases.values():
            category = case.failure_category
            if category is None:
                continue
            # Accept either top-level enum values or suite-style names.
            for member in FailureCategory:
                if category == member.value or category.startswith(f"{member.value}_"):
                    found.add(member)
                    break
        return found
