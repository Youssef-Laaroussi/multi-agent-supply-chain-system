"""
Official LangChain tools package for the Multi-Agent Supply Chain System.
All tools are instances of langchain_core.tools.BaseTool via the @tool decorator.
"""

from src.supply_chain.tools.forecasting_tools import calculate_demand_forecast_tool
from src.supply_chain.tools.inventory_tools import calculate_inventory_metrics_tool
from src.supply_chain.tools.risk_radar_tools import query_risk_radar_tool
from src.supply_chain.tools.supplier_tools import evaluate_supplier_proposals_tool
from src.supply_chain.tools.logistics_tools import plan_freight_dispatch_tool

# Backward compatibility aliases
calculate_demand_forecast = calculate_demand_forecast_tool.invoke
calculate_inventory_metrics = calculate_inventory_metrics_tool.invoke
query_risk_radar = query_risk_radar_tool.invoke
evaluate_supplier_proposals = evaluate_supplier_proposals_tool.invoke
plan_freight_dispatch = plan_freight_dispatch_tool.invoke

__all__ = [
    "calculate_demand_forecast_tool",
    "calculate_inventory_metrics_tool",
    "query_risk_radar_tool",
    "evaluate_supplier_proposals_tool",
    "plan_freight_dispatch_tool",
    "calculate_demand_forecast",
    "calculate_inventory_metrics",
    "query_risk_radar",
    "evaluate_supplier_proposals",
    "plan_freight_dispatch",
]
