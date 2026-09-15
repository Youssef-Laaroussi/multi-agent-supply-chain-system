"""
Logistics and Freight Routing Tools.

Selects carriers, determines transit schedules, calculates transportation costs,
and verifies security accreditations for strategic cargo.
"""

from typing import Dict, List, Optional
from src.supply_chain.config import CARRIER_CATALOG


def plan_freight_dispatch(
    quantity_units: int,
    urgency_level: str = "HIGH",
    require_security_escort: bool = True,
) -> Dict:
    """
    Allocates carrier and builds shipment plan based on urgency and security requirements.

    Args:
        quantity_units (int): Number of units to transport.
        urgency_level (str): "CRITICAL", "HIGH", or "STANDARD".
        require_security_escort (bool): Whether sovereign strategic security is mandatory.

    Returns:
        Dict: Full freight allocation plan including carrier, cost, and ETA.
    """
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
