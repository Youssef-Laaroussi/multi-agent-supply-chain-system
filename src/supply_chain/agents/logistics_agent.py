"""
Logistics & Fleet Orchestration Agent Node.

Adheres to LangChain & LangGraph standards:
- Invokes official `@tool` (`plan_freight_dispatch_tool`)
- Synthesizes freight allocation via LangChain ChatModel (`get_agent_llm`)
- Returns official `AIMessage` instances
"""

from datetime import datetime
from typing import Any, Dict
from langchain_core.messages import AIMessage
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.logistics_tools import plan_freight_dispatch_tool


def logistics_orchestration_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    LangGraph node: Formulates the transportation and dispatch plan.

    Args:
        state (SupplyChainState): Current workflow state with approved procurement.

    Returns:
        Dict[str, Any]: Partial state update with logistics_plan and AIMessage.
    """
    selected_procurement = state.get("selected_procurement") or {}
    quantity = selected_procurement.get("quantity_quoted", 1000)

    inventory_data = state.get("inventory_analysis", {})
    is_urgent = inventory_data.get("strategic_reserve_breach", True)
    urgency = "CRITICAL" if is_urgent else "STANDARD"

    # 1. Invoke official LangChain BaseTool
    dispatch_plan = plan_freight_dispatch_tool.invoke({
        "quantity_units": quantity,
        "urgency_level": urgency,
        "require_security_escort": True,
    })

    reasoning = (
        f"[LOGISTICS AGENT] Freight allocated for {quantity} units. Urgency: {urgency}. "
        f"Assigned carrier: {dispatch_plan['carrier_name']} ({dispatch_plan['speed_tier']}). "
        f"Transit ETA: {dispatch_plan['transit_days']} days. "
        f"Freight cost: {dispatch_plan['total_freight_cost_eur']:,.2f} EUR. "
        f"Sovereign security escort: Confirmed."
    )

    ai_message = AIMessage(content=reasoning, name="Logistics_Fleet_Agent")
    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] 🚚 LOGISTICS_AGENT: "
        f"Carrier: {dispatch_plan['carrier_name']} | Transit: {dispatch_plan['transit_days']}d | "
        f"Freight: {dispatch_plan['total_freight_cost_eur']:,.2f} EUR."
    )

    return {
        "logistics_plan": dispatch_plan,
        "current_step": "LOGISTICS_PLANNED",
        "agent_logs": [log_entry],
        "messages": [ai_message],
    }
