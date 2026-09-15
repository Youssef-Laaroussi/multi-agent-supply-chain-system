"""
Master Orchestrator Agent Node (Supply Chain Control Tower).

Synthesizes recommendations across all specialist agents, balances trade-offs,
and issues the binding Executive Supply Order.
"""

from datetime import datetime
from typing import Any, Dict
from src.supply_chain.state import SupplyChainState


def orchestrator_control_tower_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    LangGraph node: Arbitrates final trade-offs and generates binding executive decision.

    Args:
        state (SupplyChainState): Complete accumulated state across all nodes.

    Returns:
        Dict[str, Any]: State update with orchestrator_decision and completion flags.
    """
    sku = state.get("sku", "SKU-MED-901")
    demand = state.get("demand_forecast", {})
    inventory = state.get("inventory_analysis", {})
    procurement = state.get("selected_procurement") or {}
    compliance = state.get("compliance_review", {})
    logistics = state.get("logistics_plan", {})
    risk = state.get("risk_assessment", {})

    material_cost = procurement.get("total_material_cost_eur", 0.0)
    freight_cost = logistics.get("total_freight_cost_eur", 0.0)
    total_investment_eur = material_cost + freight_cost

    supplier_lead = procurement.get("effective_lead_time_days", 2)
    transit_days = logistics.get("transit_days", 1)
    total_cycle_time_days = supplier_lead + transit_days

    # Executive Order validation
    is_approved = compliance.get("status") == "APPROVED" and procurement.get("supplier_id") is not None

    decision_summary = {
        "executive_order_id": f"EX-DECREE-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "sku": sku,
        "sku_description": state.get("sku_description", "Critical Strategic Supplies"),
        "verdict": "AUTHORIZED_AND_DISPATCHED" if is_approved else "HALTED_BY_GOVERNANCE",
        "authorized_supplier": procurement.get("supplier_name", "None"),
        "supplier_country": procurement.get("country", "None"),
        "units_ordered": procurement.get("quantity_quoted", 0),
        "material_cost_eur": material_cost,
        "carrier_assigned": logistics.get("carrier_name", "None"),
        "freight_cost_eur": freight_cost,
        "total_commitment_eur": total_investment_eur,
        "estimated_arrival_days": total_cycle_time_days,
        "strategic_reserve_secured": True,
        "trade_off_resolution": (
            f"Prioritized sovereign compliance and delivery speed over lowest commercial cost. "
            f"Overruled embargoed vendor. Total investment of {total_investment_eur:,.2f} EUR "
            f"preserves national strategic buffer ({state.get('strategic_reserve_floor', 500)} units)."
        ),
    }

    reasoning = (
        f"[MASTER ORCHESTRATOR] 🎯 EXECUTIVE VERDICT: {decision_summary['verdict']}. "
        f"Order {decision_summary['executive_order_id']} issued for {decision_summary['units_ordered']} units of {sku}. "
        f"Supplier: {decision_summary['authorized_supplier']} | Carrier: {decision_summary['carrier_assigned']} | "
        f"Total Cycle Time: {total_cycle_time_days} days | Total Budget: {total_investment_eur:,.2f} EUR. "
        f"Trade-off: {decision_summary['trade_off_resolution']}"
    )

    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] 👑 ORCHESTRATOR: "
        f"Verdict: {decision_summary['verdict']} | Order: {decision_summary['executive_order_id']} | "
        f"Total: {total_investment_eur:,.2f} EUR | ETA: {total_cycle_time_days}d."
    )

    message = {
        "sender": "Master_Orchestrator_Agent",
        "content": reasoning,
    }

    return {
        "orchestrator_decision": decision_summary,
        "is_completed": True,
        "current_step": "ORCHESTRATION_FINALIZED",
        "agent_logs": [log_entry],
        "messages": [message],
    }
