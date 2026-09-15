"""
Demand Forecasting Agent Node.

Adheres to LangChain & LangGraph standards:
- Invokes official `@tool` (`calculate_demand_forecast_tool`)
- Synthesizes insights via LangChain ChatModel (`get_agent_llm`)
- Returns official `AIMessage` instances for state message history
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
    LangGraph node: Computes demand forecast for the active SKU.

    Args:
        state (SupplyChainState): Current workflow state.

    Returns:
        Dict[str, Any]: Partial state update with demand_forecast and AIMessage.
    """
    sku = state.get("sku", "SKU-MED-901")
    
    # 1. Invoke official LangChain BaseTool
    forecast_data = calculate_demand_forecast_tool.invoke({
        "sku": sku,
        "historical_consumption": [120, 115, 130, 125, 140, 110, 135],
        "growth_multiplier": 1.1,
        "emergency_shock_factor": 0.80,
    })

    # 2. Synthesize via LLM
    llm = get_agent_llm(temperature=0.0)
    system_msg = SystemMessage(content=DEMAND_AGENT_PROMPT)
    user_context = (
        f"Analyze demand for SKU {sku}. Baseline: {forecast_data['baseline_daily_average']} units/day. "
        f"Emergency shock factor: {forecast_data['surge_percentage']}. "
        f"Total projected demand: {forecast_data['total_projected_demand']} units over 7 days."
    )
    llm_response = llm.invoke([system_msg, AIMessage(content=user_context)])

    reasoning = (
        f"[DEMAND AGENT] Evaluated SKU {sku}. Baseline daily average: {forecast_data['baseline_daily_average']} units. "
        f"Critical emergency surge detected (+{forecast_data['surge_percentage']}). "
        f"Projected consumption over 7 days: {forecast_data['total_projected_demand']} units "
        f"({forecast_data['adjusted_daily_forecast']} units/day)."
    )

    ai_message = AIMessage(content=reasoning, name="Demand_Forecasting_Agent")
    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] 📈 DEMAND_AGENT: "
        f"Surge detected (+{forecast_data['surge_percentage']}). "
        f"Total 7-day demand: {forecast_data['total_projected_demand']} units."
    )

    return {
        "demand_forecast": forecast_data,
        "current_step": "DEMAND_FORECAST_COMPLETED",
        "agent_logs": [log_entry],
        "messages": [ai_message],
    }
