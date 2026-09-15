"""
Forecasting Tools for Demand Agent.

Provides statistical calculations, historical moving averages, and anomaly detection.
"""

from typing import Dict, List


def calculate_demand_forecast(
    historical_consumption: List[int],
    growth_multiplier: float = 1.0,
    emergency_shock_factor: float = 0.0,
) -> Dict:
    """
    Computes projected demand across the planning horizon.

    Args:
        historical_consumption (List[int]): Past consumption figures (e.g. daily units).
        growth_multiplier (float): Seasonal or macro trend multiplier.
        emergency_shock_factor (float): Unexpected surge factor (e.g., 0.80 for +80% surge).

    Returns:
        Dict containing projected daily consumption, total demand, and surge details.
    """
    if not historical_consumption:
        historical_consumption = [100, 110, 105, 95, 120, 100, 115]

    avg_baseline = sum(historical_consumption) / len(historical_consumption)
    adjusted_daily = avg_baseline * growth_multiplier * (1.0 + emergency_shock_factor)
    planning_horizon_days = 7
    total_projected_demand = int(adjusted_daily * planning_horizon_days)

    anomaly_detected = emergency_shock_factor > 0.25

    return {
        "baseline_daily_average": round(avg_baseline, 2),
        "adjusted_daily_forecast": round(adjusted_daily, 2),
        "planning_horizon_days": planning_horizon_days,
        "total_projected_demand": total_projected_demand,
        "emergency_shock_factor": emergency_shock_factor,
        "surge_percentage": f"{int(emergency_shock_factor * 100)}%",
        "anomaly_detected": anomaly_detected,
    }
