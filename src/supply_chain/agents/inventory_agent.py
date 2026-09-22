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
from src.supply_chain.agents.agent_factory import build_react_agent

def inventory_optimization_node(state: SupplyChainState) -> Dict[str, Any]:
    current_stock = state.get("current_inventory", 750)
    reserve_floor = state.get("strategic_reserve_floor", SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR)
    demand_data = state.get("demand_forecast", {})
    daily_demand = demand_data.get("adjusted_daily_forecast", 247.5)

    context = f"\n\nContext:\nCurrent Stock: {current_stock}\nDaily Demand: {daily_demand}\nStrategic Reserve Floor: {reserve_floor}"
    system_msg = SystemMessage(content=INVENTORY_AGENT_PROMPT.format(reserve_floor=reserve_floor) + context)
    
    agent = build_react_agent([calculate_inventory_metrics_tool])
    result = agent.invoke({"messages": [system_msg] + state.get("messages", [])})
    
    inventory_metrics = {}
    for msg in result["messages"]:
        if isinstance(msg, ToolMessage) and msg.name == "calculate_inventory_metrics_tool":
            try:
                inventory_metrics = json.loads(msg.content)
            except json.JSONDecodeError:
                pass

    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 📦 INVENTORY_AGENT: Evaluated stock."
    if inventory_metrics:
        breach = inventory_metrics.get('strategic_reserve_breach', False)
        qty = inventory_metrics.get('recommended_reorder_qty', 0)
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 📦 INVENTORY_AGENT: Stock: {current_stock}u | Breach: {breach} | Reorder: {qty} units."

    new_messages = result["messages"][len(state.get("messages", [])) + 1:] 
    
    return {
        "inventory_analysis": inventory_metrics,
        "current_step": "INVENTORY_ANALYSIS_COMPLETED",
        "agent_logs": [log_entry],
        "messages": new_messages,
    }

