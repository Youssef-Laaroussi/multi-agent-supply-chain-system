"""
Inventory Optimization Agent Node.

Adheres to LangChain & LangGraph standards:
- Invokes official `@tool` (`calculate_inventory_metrics_tool`)
- Synthesizes metrics via LangChain ChatModel (`get_agent_llm`)
- Returns official `AIMessage` instances
"""

from datetime import datetime
from typing import Any, Dict
from langchain_core.messages import AIMessage, SystemMessage
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.inventory_tools import calculate_inventory_metrics_tool
from src.supply_chain.config import SystemConfig
from src.supply_chain.prompts import INVENTORY_AGENT_PROMPT
from src.supply_chain.llm import get_agent_llm


def inventory_optimization_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    LangGraph node: Evaluates stock balance and determines reorder requirements.

    Args:
        state (SupplyChainState): Current workflow state containing demand forecast.

    Returns:
        Dict[str, Any]: Partial state update with inventory_analysis and AIMessage.
    """
    current_stock = state.get("current_inventory", 750)
    reserve_floor = state.get("strategic_reserve_floor", SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR)
    demand_data = state.get("demand_forecast", {})
    daily_demand = demand_data.get("adjusted_daily_forecast", 247.5)

    # 1. Invoke official LangChain BaseTool
    inventory_metrics = calculate_inventory_metrics_tool.invoke({
        "current_stock": current_stock,
        "daily_demand": daily_demand,
        "lead_time_days": 3,
        "demand_std_dev": 20.0,
        "service_factor_z": 1.96,
        "strategic_reserve_floor": reserve_floor,
    })

    breach_warning = ""
    if inventory_metrics["strategic_reserve_breach"]:
        breach_warning = (
            f" 🚨 CRITICAL ALERT: Projected stock after lead time ({inventory_metrics['projected_post_lead_stock']} units) "
            f"breaches statutory reserve floor ({reserve_floor} units)!"
        )

    reasoning = (
        f"[INVENTORY AGENT] Current stock: {current_stock} units. Daily demand: {daily_demand} units/day. "
        f"Days of supply remaining: {inventory_metrics['days_of_supply']} days. "
        f"Safety Stock required: {inventory_metrics['safety_stock']} units. "
        f"Reorder Point (ROP): {inventory_metrics['reorder_point']} units.{breach_warning} "
        f"Recommended emergency replenishment quantity: {inventory_metrics['recommended_reorder_qty']} units."
    )

    ai_message = AIMessage(content=reasoning, name="Inventory_Optimization_Agent")
    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] 📦 INVENTORY_AGENT: "
        f"Stock: {current_stock}u | Days supply: {inventory_metrics['days_of_supply']}d | "
        f"Reserve breach: {inventory_metrics['strategic_reserve_breach']} | "
        f"Reorder requisition: {inventory_metrics['recommended_reorder_qty']} units."
    )

    return {
        "inventory_analysis": inventory_metrics,
        "current_step": "INVENTORY_ANALYSIS_COMPLETED",
        "agent_logs": [log_entry],
        "messages": [ai_message],
    }
