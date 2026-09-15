"""
Procurement and Supplier Evaluation Tools.

Queries approved vendor catalogs, factors in dynamic risk delays,
computes total landed item costs, and formats supplier bids.
"""

from typing import Dict, List, Optional
from src.supply_chain.config import SUPPLIER_CATALOG


def evaluate_supplier_proposals(
    quantity_needed: int,
    disruptions: Optional[List[Dict]] = None,
) -> List[Dict]:
    """
    Evaluates available suppliers from catalog and calculates adjusted lead times and costs.

    Args:
        quantity_needed (int): Required units for replenishment.
        disruptions (Optional[List[Dict]]): Active disruption events affecting suppliers.

    Returns:
        List[Dict]: Comprehensive list of vendor quotes with adjusted lead times.
    """
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
