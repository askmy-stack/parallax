"""Customer service API environment with versioned tool contracts."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Literal

from runtime.schemas.episode import Action, EnvObservation, TaskSpec

ContractVersion = Literal["v1", "v2"]

# v1: plan_id means billing_plan_code (canonical)
# v2: plan_id means sku_variant (same JSON field, different meaning)
PLAN_CATALOG_V1: dict[str, dict[str, Any]] = {
    "BASIC_MONTHLY": {
        "plan_id": "BASIC_MONTHLY",
        "plan_name": "Basic Monthly",
        "billing_plan_code": "BASIC_MONTHLY",
        "sku_variant": "SKU_BASIC_M",
    },
    "GOLD_ANNUAL": {
        "plan_id": "GOLD_ANNUAL",
        "plan_name": "Gold Annual",
        "billing_plan_code": "GOLD_ANNUAL",
        "sku_variant": "SKU_GOLD_A",
    },
}

PLAN_CATALOG_V2: dict[str, dict[str, Any]] = {
    "SKU_BASIC_M": {
        "plan_id": "SKU_BASIC_M",
        "plan_name": "Basic Blue (M)",
        "billing_plan_code": "BASIC_MONTHLY",
        "sku_variant": "SKU_BASIC_M",
    },
    "SKU_GOLD_A": {
        "plan_id": "SKU_GOLD_A",
        "plan_name": "Gold Blue (A)",
        "billing_plan_code": "GOLD_ANNUAL",
        "sku_variant": "SKU_GOLD_A",
    },
    # Trap: agent may still send billing codes after drift
    "GOLD_ANNUAL": {
        "plan_id": "GOLD_ANNUAL",
        "plan_name": "Misinterpreted SKU-looking code",
        "billing_plan_code": "BASIC_MONTHLY",
        "sku_variant": "GOLD_ANNUAL",
    },
}


def plan_id_meaning(version: ContractVersion) -> str:
    return "billing_plan_code" if version == "v1" else "sku_variant"


@dataclass
class CustomerApiEnv:
    """Deterministic in-memory customer subscription API."""

    task: TaskSpec
    contract_version: ContractVersion = "v1"
    store: dict[str, Any] = field(default_factory=dict)
    call_count: int = 0

    def __post_init__(self) -> None:
        if not self.store:
            self.store = {
                "customers": {
                    self.task.customer_id: {
                        "customer_id": self.task.customer_id,
                        "name": "Ada Lovelace",
                    }
                },
                "subscriptions": {
                    self.task.customer_id: {
                        "customer_id": self.task.customer_id,
                        "subscription_id": "sub_001",
                        "billing_plan_code": "BASIC_MONTHLY",
                        "sku_variant": "SKU_BASIC_M",
                    }
                },
            }

    @property
    def catalog(self) -> dict[str, dict[str, Any]]:
        return PLAN_CATALOG_V1 if self.contract_version == "v1" else PLAN_CATALOG_V2

    def set_contract(self, version: ContractVersion) -> None:
        self.contract_version = version

    def reset(self) -> None:
        self.call_count = 0
        self.contract_version = "v1"
        self.store = {
            "customers": {
                self.task.customer_id: {
                    "customer_id": self.task.customer_id,
                    "name": "Ada Lovelace",
                }
            },
            "subscriptions": {
                self.task.customer_id: {
                    "customer_id": self.task.customer_id,
                    "subscription_id": "sub_001",
                    "billing_plan_code": "BASIC_MONTHLY",
                    "sku_variant": "SKU_BASIC_M",
                }
            },
        }

    def step(self, action: Action) -> EnvObservation:
        self.call_count += 1
        name = action.name
        args = action.arguments
        if name == "get_customer":
            customer = self.store["customers"].get(args.get("customer_id"))
            if customer is None:
                return EnvObservation(success=False, status_code=404, error="customer_not_found")
            return EnvObservation(success=True, data=deepcopy(customer))
        if name == "get_subscription":
            sub = self.store["subscriptions"].get(args.get("customer_id"))
            if sub is None:
                return EnvObservation(
                    success=False, status_code=404, error="subscription_not_found"
                )
            payload = deepcopy(sub)
            # Surface plan_id using active contract semantics
            if self.contract_version == "v1":
                payload["plan_id"] = payload["billing_plan_code"]
            else:
                payload["plan_id"] = payload["sku_variant"]
            payload["plan_id_meaning"] = plan_id_meaning(self.contract_version)
            payload["contract_version"] = self.contract_version
            return EnvObservation(success=True, data=payload)
        if name == "get_plan":
            plan_id = str(args.get("plan_id", ""))
            plan = self.catalog.get(plan_id)
            if plan is None:
                return EnvObservation(
                    success=False, status_code=404, error="plan_not_found", data={}
                )
            payload = deepcopy(plan)
            payload["plan_id_meaning"] = plan_id_meaning(self.contract_version)
            payload["contract_version"] = self.contract_version
            return EnvObservation(success=True, data=payload)
        if name == "update_subscription":
            customer_id = str(args.get("customer_id", ""))
            plan_id = str(args.get("plan_id", ""))
            sub = self.store["subscriptions"].get(customer_id)
            if sub is None:
                return EnvObservation(
                    success=False, status_code=404, error="subscription_not_found"
                )
            plan = self.catalog.get(plan_id)
            if plan is None:
                return EnvObservation(success=False, status_code=400, error="invalid_plan_id")
            # Apply using active contract meaning
            if self.contract_version == "v1":
                sub["billing_plan_code"] = plan["billing_plan_code"]
                sub["sku_variant"] = plan["sku_variant"]
            else:
                # v2: plan_id is sku_variant; map to billing code via catalog
                sub["sku_variant"] = plan["sku_variant"]
                sub["billing_plan_code"] = plan["billing_plan_code"]
            return EnvObservation(
                success=True,
                data={
                    "customer_id": customer_id,
                    "plan_id": plan_id,
                    "billing_plan_code": sub["billing_plan_code"],
                    "sku_variant": sub["sku_variant"],
                    "plan_id_meaning": plan_id_meaning(self.contract_version),
                    "contract_version": self.contract_version,
                    "updated": True,
                },
            )
        if name == "refresh_tool_contract":
            version = args.get("version", "v2")
            if version not in ("v1", "v2"):
                return EnvObservation(success=False, status_code=400, error="invalid_version")
            assert version in ("v1", "v2")
            self.set_contract(version)
            return EnvObservation(
                success=True,
                data={
                    "contract_version": self.contract_version,
                    "plan_id_meaning": plan_id_meaning(self.contract_version),
                },
            )
        return EnvObservation(success=False, status_code=400, error=f"unknown_action:{name}")

    def validate_success(self) -> bool:
        """True if subscription billing_plan_code matches the task target."""
        sub = self.store["subscriptions"].get(self.task.customer_id)
        if sub is None:
            return False
        return str(sub["billing_plan_code"]) == self.task.target_plan_code

    def expected_plan_id_for_agent(self) -> str:
        """What a v1-trained agent believes it should send as plan_id."""
        return self.task.target_plan_code

    def true_plan_id_under_contract(self) -> str:
        """Correct plan_id argument under the current contract."""
        if self.contract_version == "v1":
            return self.task.target_plan_code
        # Map billing code → sku for v2
        for plan in PLAN_CATALOG_V1.values():
            if plan["billing_plan_code"] == self.task.target_plan_code:
                return str(plan["sku_variant"])
        return self.task.target_plan_code
