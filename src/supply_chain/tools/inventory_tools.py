"""
Inventory Optimization Tools.

Provides deterministic calculations for Safety Stock, Reorder Point (ROP),
stockout timelines, and breach checks against State Strategic Reserve Floors.
"""

import math
from typing import Dict


def calculate_inventory_metrics(
    current_stock: int,
    daily_demand: float,
    lead_time_days: int = 3,
    demand_std_dev: float = 15.0,
    service_factor_z: float = 1.96,  # 97.5% Service Level
    strategic_reserve_floor: int = 500,
) -> Dict:
    """
    Evaluates inventory health against standard replenishment metrics and sovereign floors.

    Args:
        current_stock (int): Physical units on hand.
        daily_demand (float): Projected units consumed per day.
        lead_time_days (int): Expected supplier replenishment time.
        demand_std_dev (float): Standard deviation of daily demand.
        service_factor_z (float): Z-score for target service level.
        strategic_reserve_floor (int): Minimum untouchable state stock.

    Returns:
        Dict of metrics including safety stock, ROP, days of supply, and breach flags.
    """
    safety_stock = int(service_factor_z * demand_std_dev * math.sqrt(lead_time_days))
    lead_time_demand = daily_demand * lead_time_days
    reorder_point = int(lead_time_demand + safety_stock)

    days_of_supply = round(current_stock / daily_demand, 1) if daily_demand > 0 else 999.0

    # Project stock after lead time consumption
    projected_post_lead_stock = int(current_stock - lead_time_demand)
    strategic_breach = projected_post_lead_stock < strategic_reserve_floor

    # Recommended replenishment quantity (target: restore buffer + 7 days operating cycle)
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
