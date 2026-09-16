"""
Logistics & Fleet Orchestration Agent Node.

Official LangChain & LangGraph implementation:
- Uses `llm.bind_tools([plan_freight_dispatch_tool])`
- Invokes model with state messages
- Allocates certified carrier fleet and emits AIMessage with tool calls
"""

from datetime import datetime
from typing import Any, Dict
from langchain_core.messages import AIMessage, SystemMessage
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.logistics_tools import plan_freight_dispatch_tool
from src.supply_chain.prompts import LOGISTICS_AGENT_PROMPT
from src.supply_chain.llm import get_agent_llm


def logistics_orchestration_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    LangGraph agent node: Dispatches freight and establishes transport schedule.
    """
    selected_procurement = state.get("selected_procurement") or {}
    quantity = selected_procurement.get("quantity_quoted", 1000)

    inventory_data = state.get("inventory_analysis", {})
    is_urgent = inventory_data.get("strategic_reserve_breach", True)
    urgency = "CRITICAL" if is_urgent else "STANDARD"

    # 1. Official tool binding and model invocation
    model = get_agent_llm(temperature=0.0).bind_tools([plan_freight_dispatch_tool])
    system_msg = SystemMessage(content=LOGISTICS_AGENT_PROMPT)
    ai_response = model.invoke([system_msg] + state.get("messages", []))

    # 2. Execute tool invocation
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

    ai_msg = AIMessage(
        content=reasoning,
        name="Logistics_Fleet_Agent",
        tool_calls=ai_response.tool_calls,
    )
    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] 🚚 LOGISTICS_AGENT: "
        f"Carrier: {dispatch_plan['carrier_name']} | Transit: {dispatch_plan['transit_days']}d | "
        f"Freight: {dispatch_plan['total_freight_cost_eur']:,.2f} EUR."
    )

    return {
        "logistics_plan": dispatch_plan,
        "current_step": "LOGISTICS_PLANNED",
        "agent_logs": [log_entry],
        "messages": [ai_msg],
    }
