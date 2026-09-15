"""
Official LangChain Tools for Inventory Optimization.

Uses `@tool` decorator with explicit Pydantic `args_schema` for LLM tool binding.
"""

import math
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from src.supply_chain.config import SystemConfig


class InventoryMetricsInput(BaseModel):
    """Input schema for inventory calculation tool."""
    current_stock: int = Field(description="Current physical units available in warehouse")
    daily_demand: float = Field(description="Projected average daily units consumed")
    lead_time_days: int = Field(default=3, description="Expected replenishment lead time in days")
    demand_std_dev: float = Field(default=15.0, description="Standard deviation of daily consumption")
    service_factor_z: float = Field(default=1.96, description="Z-score for target service level (1.96 = 97.5%)")
    strategic_reserve_floor: int = Field(
        default=SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR,
        description="Statutory non-negotiable state strategic reserve floor"
    )


@tool(args_schema=InventoryMetricsInput)
def calculate_inventory_metrics_tool(
    current_stock: int,
    daily_demand: float,
    lead_time_days: int = 3,
    demand_std_dev: float = 15.0,
    service_factor_z: float = 1.96,
    strategic_reserve_floor: int = SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR,
) -> dict:
    """Calculate Reorder Point (ROP), Safety Stock (SS), and audit against the State Strategic Reserve Floor."""
    safety_stock = int(service_factor_z * demand_std_dev * math.sqrt(lead_time_days))
    lead_time_demand = daily_demand * lead_time_days
    reorder_point = int(lead_time_demand + safety_stock)
    days_of_supply = round(current_stock / daily_demand, 1) if daily_demand > 0 else 999.0

    projected_post_lead_stock = int(current_stock - lead_time_demand)
    strategic_breach = projected_post_lead_stock < strategic_reserve_floor

    recommended_reorder = max(
        0,
        int((strategic_reserve_floor + (daily_demand * 7) + safety_stock) - current_stock),
    )

    return {
        "current_stock": current_stock,
        "strategic_reserve_floor": strategic_reserve_floor,
        "daily_demand": round(daily_demand, 2),
        "lead_time_days": lead_time_days,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "days_of_supply": days_of_supply,
        "projected_post_lead_stock": projected_post_lead_stock,
        "strategic_reserve_breach": strategic_breach,
        "reorder_needed": current_stock <= reorder_point or strategic_breach,
        "recommended_reorder_qty": recommended_reorder,
    }
