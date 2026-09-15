"""
Official LangChain Tools for Demand Forecasting.

Uses `@tool` decorator with explicit Pydantic `args_schema` for LLM tool binding.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool


class DemandForecastInput(BaseModel):
    """Input schema for demand forecasting tool."""
    sku: str = Field(description="The unique identifier for the strategic product, e.g. SKU-MED-901")
    historical_consumption: Optional[List[int]] = Field(
        default=None,
        description="List of recent historical consumption quantities (daily units)"
    )
    growth_multiplier: float = Field(
        default=1.0,
        description="Macro-economic or seasonal growth factor (default 1.0)"
    )
    emergency_shock_factor: float = Field(
        default=0.0,
        description="Crisis surge multiplier (e.g. 0.80 for +80% unexpected surge)"
    )


@tool(args_schema=DemandForecastInput)
def calculate_demand_forecast_tool(
    sku: str,
    historical_consumption: Optional[List[int]] = None,
    growth_multiplier: float = 1.0,
    emergency_shock_factor: float = 0.0,
) -> dict:
    """Calculate statistical demand projections and detect consumption anomalies for a strategic SKU."""
    if not historical_consumption:
        historical_consumption = [100, 110, 105, 95, 120, 100, 115]

    avg_baseline = sum(historical_consumption) / len(historical_consumption)
    adjusted_daily = avg_baseline * growth_multiplier * (1.0 + emergency_shock_factor)
    planning_horizon_days = 7
    total_projected_demand = int(adjusted_daily * planning_horizon_days)
    anomaly_detected = emergency_shock_factor > 0.25

    return {
        "sku": sku,
        "baseline_daily_average": round(avg_baseline, 2),
        "adjusted_daily_forecast": round(adjusted_daily, 2),
        "planning_horizon_days": planning_horizon_days,
        "total_projected_demand": total_projected_demand,
        "emergency_shock_factor": emergency_shock_factor,
        "surge_percentage": f"{int(emergency_shock_factor * 100)}%",
        "anomaly_detected": anomaly_detected,
    }
