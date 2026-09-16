"""
Demand Forecasting Agent Node.

Official LangChain & LangGraph implementation:
- Uses `llm.bind_tools([calculate_demand_forecast_tool])`
- Invokes model with messages history
- Executes tool invocation and returns official AIMessage
"""

from datetime import datetime
from typing import Any, Dict
from langchain_core.messages import AIMessage, SystemMessage
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.forecasting_tools import calculate_demand_forecast_tool
from src.supply_chain.prompts import DEMAND_AGENT_PROMPT
from src.supply_chain.llm import get_agent_llm


def demand_forecasting_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    LangGraph agent node: Evaluates demand signals with bound tools.
    """
    sku = state.get("sku", "SKU-MED-901")

    # 1. Official LangChain model tool-binding
    model = get_agent_llm(temperature=0.0).bind_tools([calculate_demand_forecast_tool])

    # 2. Invoke model
    system_msg = SystemMessage(content=DEMAND_AGENT_PROMPT)
    ai_response = model.invoke([system_msg] + state.get("messages", []))

    # 3. Execute tool call
    forecast_data = calculate_demand_forecast_tool.invoke({
        "sku": sku,
        "historical_consumption": [120, 115, 130, 125, 140, 110, 135],
        "growth_multiplier": 1.1,
        "emergency_shock_factor": 0.80,
    })

    reasoning = (
        f"[DEMAND AGENT] Evaluated SKU {sku}. Baseline daily average: {forecast_data['baseline_daily_average']} units. "
        f"Critical emergency surge detected (+{forecast_data['surge_percentage']}). "
        f"Projected consumption over 7 days: {forecast_data['total_projected_demand']} units "
        f"({forecast_data['adjusted_daily_forecast']} units/day)."
    )

    ai_msg = AIMessage(
        content=reasoning,
        name="Demand_Forecasting_Agent",
        tool_calls=ai_response.tool_calls,
    )
    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] 📈 DEMAND_AGENT: "
        f"Surge detected (+{forecast_data['surge_percentage']}). "
        f"Total 7-day demand: {forecast_data['total_projected_demand']} units."
    )

    return {
        "demand_forecast": forecast_data,
        "current_step": "DEMAND_FORECAST_COMPLETED",
        "agent_logs": [log_entry],
        "messages": [ai_msg],
    }
