"""
Official LangChain Tools for Logistics & Fleet Freight Planning.

Uses `@tool` decorator with explicit Pydantic `args_schema` for LLM tool binding.
"""

from pydantic import BaseModel, Field
from langchain_core.tools import tool
from src.supply_chain.config import CARRIER_CATALOG


class FreightDispatchInput(BaseModel):
    """Input schema for freight dispatch planning tool."""
    quantity_units: int = Field(description="Total number of units to be loaded and dispatched")
    urgency_level: str = Field(
        default="HIGH",
        description="Urgency tier: 'CRITICAL', 'HIGH', or 'STANDARD'"
    )
    require_security_escort: bool = Field(
        default=True,
        description="Mandatory state security escort certification for strategic goods"
    )


@tool(args_schema=FreightDispatchInput)
def plan_freight_dispatch_tool(
    quantity_units: int,
    urgency_level: str = "HIGH",
    require_security_escort: bool = True,
) -> dict:
    """Select security-certified carrier fleet, calculate freight costs, and establish dock ETA."""
    selected_carrier = None
    for carrier in CARRIER_CATALOG:
        if require_security_escort and not carrier["certified_security"]:
            continue

        if urgency_level in ("CRITICAL", "HIGH") and carrier["speed_tier"] == "CRITICAL_EXPRESS":
            selected_carrier = carrier
            break
        elif urgency_level == "STANDARD" and carrier["speed_tier"] == "STANDARD_ROAD":
            selected_carrier = carrier
            break

    # Fallback to first certified carrier
    if not selected_carrier:
        for carrier in CARRIER_CATALOG:
            if not require_security_escort or carrier["certified_security"]:
                selected_carrier = carrier
                break

    freight_cost = round(quantity_units * selected_carrier["cost_per_unit_eur"], 2)

    return {
        "carrier_id": selected_carrier["id"],
        "carrier_name": selected_carrier["name"],
        "speed_tier": selected_carrier["speed_tier"],
        "transit_days": selected_carrier["transit_days"],
        "cost_per_unit_eur": selected_carrier["cost_per_unit_eur"],
        "total_freight_cost_eur": freight_cost,
        "security_certified": selected_carrier["certified_security"],
        "escort_assigned": require_security_escort,
        "dispatch_status": "READY_FOR_MANIFEST",
    }
