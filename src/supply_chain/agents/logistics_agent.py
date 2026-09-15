"""
Logistics & Fleet Orchestration Agent Node.

Plans cargo transit, selects certified carrier fleets, and schedules freight dispatch.
"""

from datetime import datetime
from typing import Any, Dict
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.logistics_tools import plan_freight_dispatch


def logistics_orchestration_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    LangGraph node: Formulates the transportation and dispatch plan.

    Args:
        state (SupplyChainState): Current workflow state with approved procurement.

    Returns:
        Dict[str, Any]: Partial state update with logistics_plan.
    """
    selected_procurement = state.get("selected_procurement") or {}
    quantity = selected_procurement.get("quantity_quoted", 1000)

    # If strategic reserve is at risk, assign highest urgency
    inventory_data = state.get("inventory_analysis", {})
    is_urgent = inventory_data.get("strategic_reserve_breach", True)
    urgency = "CRITICAL" if is_urgent else "STANDARD"

    dispatch_plan = plan_freight_dispatch(
        quantity_units=quantity,
        urgency_level=urgency,
        require_security_escort=True,
    )

    reasoning = (
        f"[LOGISTICS AGENT] Freight allocated for {quantity} units. Urgency: {urgency}. "
        f"Assigned carrier: {dispatch_plan['carrier_name']} ({dispatch_plan['speed_tier']}). "
        f"Transit ETA: {dispatch_plan['transit_days']} days. "
        f"Freight cost: {dispatch_plan['total_freight_cost_eur']:,.2f} EUR. "
        f"Sovereign security escort: Confirmed."
    )

    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] 🚚 LOGISTICS_AGENT: "
        f"Carrier: {dispatch_plan['carrier_name']} | Transit: {dispatch_plan['transit_days']}d | "
        f"Freight: {dispatch_plan['total_freight_cost_eur']:,.2f} EUR."
    )

    message = {
        "sender": "Logistics_Fleet_Agent",
        "content": reasoning,
    }

    return {
        "logistics_plan": dispatch_plan,
        "current_step": "LOGISTICS_PLANNED",
        "agent_logs": [log_entry],
        "messages": [message],
    }
