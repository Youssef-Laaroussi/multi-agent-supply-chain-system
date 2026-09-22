"""
Logistics & Fleet Orchestration Agent Node.

Official LangChain & LangGraph implementation:
- Uses `llm.bind_tools([plan_freight_dispatch_tool])`
- Invokes model with state messages
- Allocates certified carrier fleet and emits AIMessage with tool calls
"""

import json
from datetime import datetime
from typing import Any, Dict
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.logistics_tools import plan_freight_dispatch_tool
from src.supply_chain.prompts import LOGISTICS_AGENT_PROMPT
from src.supply_chain.llm import get_agent_llm

def logistics_orchestration_node(state: SupplyChainState) -> Dict[str, Any]:
    selected_procurement = state.get("selected_procurement") or {}
    quantity = selected_procurement.get("quantity_quoted", 1000)
    inventory_data = state.get("inventory_analysis", {})
    is_urgent = inventory_data.get("strategic_reserve_breach", True)

    model = get_agent_llm(temperature=0.0).bind_tools([plan_freight_dispatch_tool])
    
    context = f"\n\nContext:\nQuantity to Dispatch: {quantity}\nStrategic Reserve Breach (Urgency): {is_urgent}"
    system_msg = SystemMessage(content=LOGISTICS_AGENT_PROMPT + context)
    messages = [system_msg] + state.get("messages", [])
    
    ai_response = model.invoke(messages)
    dispatch_plan = {}
    tool_messages = []
    log_entry = ""
    messages_to_add = [ai_response]

    if hasattr(ai_response, "tool_calls") and ai_response.tool_calls:
        for tool_call in ai_response.tool_calls:
            if tool_call["name"] == "plan_freight_dispatch_tool":
                args = tool_call["args"]
                if "quantity_units" not in args:
                    args["quantity_units"] = quantity
                
                dispatch_plan = plan_freight_dispatch_tool.invoke(args)
                tool_msg = ToolMessage(
                    content=json.dumps(dispatch_plan),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"]
                )
                tool_messages.append(tool_msg)

        if tool_messages:
            messages_to_add.extend(tool_messages)
            final_response = model.invoke(messages + messages_to_add)
            messages_to_add.append(AIMessage(content=final_response.content, name="Logistics_Agent"))
            name = dispatch_plan.get('carrier_name', 'UNKNOWN')
            transit = dispatch_plan.get('transit_days', 0)
            cost = dispatch_plan.get('total_freight_cost_eur', 0.0)
            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 🚚 LOGISTICS_AGENT: Carrier: {name} | Transit: {transit}d | Freight: {cost:,.2f} EUR."

    if not dispatch_plan:
        messages_to_add = [AIMessage(content=ai_response.content, name="Logistics_Agent")]
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 🚚 LOGISTICS_AGENT: Manual logistics evaluation without tools."

    return {
        "logistics_plan": dispatch_plan,
        "current_step": "LOGISTICS_PLANNED",
        "agent_logs": [log_entry],
        "messages": messages_to_add,
    }
