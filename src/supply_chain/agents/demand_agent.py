"""
Demand Forecasting Agent Node.

Analyzes consumption trends, emergency shock multipliers, and produces projected demand.
"""

from datetime import datetime
from typing import Any, Dict
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.forecasting_tools import calculate_demand_forecast
from src.supply_chain.prompts import DEMAND_AGENT_PROMPT


def demand_forecasting_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    LangGraph node: Computes demand forecast for the active SKU.

    Args:
        state (SupplyChainState): Current workflow state.

    Returns:
        Dict[str, Any]: Partial state update with demand_forecast and agent logs.
    """
    sku = state.get("sku", "SKU-MED-901")
    
    # Simulate an emergency shock scenario (+80% surge due to regional crisis)
    emergency_factor = 0.80
    historical_baseline = [120, 115, 130, 125, 140, 110, 135]

    forecast_data = calculate_demand_forecast(
        historical_consumption=historical_baseline,
        growth_multiplier=1.1,
        emergency_shock_factor=emergency_factor,
    )

    reasoning = (
        f"[DEMAND AGENT] Evaluated SKU {sku}. Baseline daily average: {forecast_data['baseline_daily_average']} units. "
        f"Critical emergency surge detected (+{forecast_data['surge_percentage']}). "
        f"Projected consumption over 7 days: {forecast_data['total_projected_demand']} units "
        f"({forecast_data['adjusted_daily_forecast']} units/day)."
    )

    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] 📈 DEMAND_AGENT: "
        f"Surge detected (+{forecast_data['surge_percentage']}). "
        f"Total 7-day demand: {forecast_data['total_projected_demand']} units."
    )

    message = {
        "sender": "Demand_Forecasting_Agent",
        "content": reasoning,
    }

    return {
        "demand_forecast": forecast_data,
        "current_step": "DEMAND_FORECAST_COMPLETED",
        "agent_logs": [log_entry],
        "messages": [message],
    }
