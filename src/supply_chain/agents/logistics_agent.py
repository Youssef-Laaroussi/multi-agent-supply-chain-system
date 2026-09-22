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
from src.supply_chain.agents.agent_factory import build_react_agent

def logistics_dispatch_node(state: SupplyChainState) -> Dict[str, Any]:
    procurement = state.get("selected_procurement") or {}
    inventory_data = state.get("inventory_analysis", {})
    
    quantity = procurement.get("quantity_quoted", 0)
    is_urgent = inventory_data.get("strategic_reserve_breach", False)

    context = f"\n\nContext:\nQuantity to Dispatch: {quantity}\nStrategic Reserve Breach (Urgency): {is_urgent}"
    system_msg = SystemMessage(content=LOGISTICS_AGENT_PROMPT + context)
    
    agent = build_react_agent([plan_freight_dispatch_tool])
    result = agent.invoke({"messages": [system_msg] + state.get("messages", [])})
    
    dispatch_plan = {}
    for msg in result["messages"]:
        if isinstance(msg, ToolMessage) and msg.name == "plan_freight_dispatch_tool":
            try:
                dispatch_plan = json.loads(msg.content)
            except json.JSONDecodeError:
                pass

    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 🚚 LOGISTICS_AGENT: Planning dispatched."
    if dispatch_plan:
        tier = dispatch_plan.get('urgency_tier', 'STANDARD')
        cost = dispatch_plan.get('total_freight_cost_eur', 0)
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 🚚 LOGISTICS_AGENT: Mode: {tier} | Carrier: {dispatch_plan.get('carrier_name')} | Freight: {cost} EUR."

    new_messages = result["messages"][len(state.get("messages", [])) + 1:] 
    
    return {
        "logistics_plan": dispatch_plan,
        "current_step": "LOGISTICS_PLANNING_COMPLETED",
        "agent_logs": [log_entry],
        "messages": new_messages,
    }
