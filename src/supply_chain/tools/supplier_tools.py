"""
Official LangChain Tools for Procurement & Supplier Proposal Evaluation.

Uses `@tool` decorator with explicit Pydantic `args_schema` for LLM tool binding.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from src.supply_chain.config import SUPPLIER_CATALOG


class SupplierEvaluationInput(BaseModel):
    """Input schema for supplier proposal evaluation tool."""
    quantity_needed: int = Field(description="Replenishment quantity requested by inventory planners")
    disruptions: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Active disruption alerts impacting supplier lead times"
    )


@tool(args_schema=SupplierEvaluationInput)
def evaluate_supplier_proposals_tool(
    quantity_needed: int,
    disruptions: Optional[List[Dict[str, Any]]] = None,
) -> List[dict]:
    """Retrieve vendor proposals from catalog, apply risk-induced delays, and rank quotation options."""
    disruption_delay_map = {}
    if disruptions:
        for alert in disruptions:
            supplier_id = alert.get("impacted_supplier_id")
            if supplier_id:
                disruption_delay_map[supplier_id] = alert.get("induced_delay_days", 0)

    evaluated_proposals = []
    for supplier in SUPPLIER_CATALOG:
        base_lead = supplier["lead_time_days"]
        extra_delay = disruption_delay_map.get(supplier["id"], 0)
        effective_lead_time = base_lead + extra_delay

        total_cost = round(quantity_needed * supplier["unit_price_eur"], 2)
        can_fulfill_capacity = supplier["capacity_units"] >= quantity_needed

        evaluated_proposals.append({
            "supplier_id": supplier["id"],
            "supplier_name": supplier["name"],
            "country": supplier["country"],
            "certified_by_state": supplier["certified_by_state"],
            "base_lead_time_days": base_lead,
            "disruption_delay_days": extra_delay,
            "effective_lead_time_days": effective_lead_time,
            "unit_price_eur": supplier["unit_price_eur"],
            "total_material_cost_eur": total_cost,
            "quantity_quoted": quantity_needed,
            "capacity_sufficient": can_fulfill_capacity,
            "reliability_score": supplier["reliability_score"],
            "notes": supplier["description"],
        })

    # Sort proposals by effective lead time, then reliability
    evaluated_proposals.sort(key=lambda p: (p["effective_lead_time_days"], -p["reliability_score"]))
    return evaluated_proposals
