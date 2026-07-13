"""Registry for AgentFailBench cases."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from agentfailbench.models import BenchmarkCaseModel
from runtime.schemas.taxonomy import FailureCategory


@dataclass
class BenchmarkCase:
    """Parsed AgentFailBench case definition."""

    case_id: str
    model: BenchmarkCaseModel

    @property
    def failure_category(self) -> str:
        return self.model.failure_category

    @property
    def raw(self) -> dict[str, object]:
        return self.model.to_raw()


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
        import yaml

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Case file must be a mapping: {path}")
        model = BenchmarkCaseModel.model_validate(data)
        registry = cls()
        registry.register(BenchmarkCase(case_id=model.case_id, model=model))
        return registry

    @classmethod
    def from_directory(cls, directory: Path) -> CaseRegistry:
        """Load all ``*.yaml`` / ``*.yml`` case files under ``directory`` (recursive)."""
        registry = cls()
        paths = sorted(directory.rglob("*.yaml")) + sorted(directory.rglob("*.yml"))
        for path in paths:
            if path.name.startswith("."):
                continue
            partial = cls.from_yaml_file(path)
            for case in partial.cases.values():
                registry.register(case)
        return registry

    def categories_present(self) -> set[FailureCategory]:
        """Return FailureCategory values present in registered cases when parseable."""
        found: set[FailureCategory] = set()
        for case in self.cases.values():
            category = case.failure_category
            for member in FailureCategory:
                if category == member.value or category.startswith(f"{member.value}_"):
                    found.add(member)
                    break
        return found
