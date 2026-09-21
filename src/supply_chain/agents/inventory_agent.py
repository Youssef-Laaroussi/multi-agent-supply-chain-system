"""
Inventory Optimization Agent Node.

Official LangChain & LangGraph implementation:
- Uses `llm.bind_tools([calculate_inventory_metrics_tool])`
- Invokes model with state messages
- Returns AIMessage with structured reasoning and tool calls
"""

import json
from datetime import datetime
from typing import Any, Dict
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.inventory_tools import calculate_inventory_metrics_tool
from src.supply_chain.config import SystemConfig
from src.supply_chain.prompts import INVENTORY_AGENT_PROMPT
from src.supply_chain.llm import get_agent_llm

def inventory_optimization_node(state: SupplyChainState) -> Dict[str, Any]:
    current_stock = state.get("current_inventory", 750)
    reserve_floor = state.get("strategic_reserve_floor", SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR)
    demand_data = state.get("demand_forecast", {})
    daily_demand = demand_data.get("adjusted_daily_forecast", 247.5)

    model = get_agent_llm(temperature=0.0).bind_tools([calculate_inventory_metrics_tool])
    
    context = f"\n\nContext:\nCurrent Stock: {current_stock}\nDaily Demand: {daily_demand}\nStrategic Reserve Floor: {reserve_floor}"
    system_msg = SystemMessage(content=INVENTORY_AGENT_PROMPT.format(reserve_floor=reserve_floor) + context)
    messages = [system_msg] + state.get("messages", [])
    
    ai_response = model.invoke(messages)
    inventory_metrics = {}
    tool_messages = []
    log_entry = ""
    messages_to_add = [ai_response]

    if hasattr(ai_response, "tool_calls") and ai_response.tool_calls:
        for tool_call in ai_response.tool_calls:
            if tool_call["name"] == "calculate_inventory_metrics_tool":
                args = tool_call["args"]
                if "current_stock" not in args:
                    args["current_stock"] = current_stock
                if "daily_demand" not in args:
                    args["daily_demand"] = daily_demand
                if "strategic_reserve_floor" not in args:
                    args["strategic_reserve_floor"] = reserve_floor
                
                inventory_metrics = calculate_inventory_metrics_tool.invoke(args)
                tool_msg = ToolMessage(
                    content=json.dumps(inventory_metrics),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"]
                )
                tool_messages.append(tool_msg)

        if tool_messages:
            messages_to_add.extend(tool_messages)
            final_response = model.invoke(messages + messages_to_add)
            messages_to_add.append(AIMessage(content=final_response.content, name="Inventory_Optimization_Agent"))
            breach = inventory_metrics.get('strategic_reserve_breach', False)
            qty = inventory_metrics.get('recommended_reorder_qty', 0)
            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 📦 INVENTORY_AGENT: Stock: {current_stock}u | Reserve breach: {breach} | Reorder: {qty} units."

    if not inventory_metrics:
        messages_to_add = [AIMessage(content=ai_response.content, name="Inventory_Optimization_Agent")]
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 📦 INVENTORY_AGENT: Manual inventory evaluation without tools."

    return {
        "inventory_analysis": inventory_metrics,
        "current_step": "INVENTORY_ANALYSIS_COMPLETED",
        "agent_logs": [log_entry],
        "messages": messages_to_add,
    }
