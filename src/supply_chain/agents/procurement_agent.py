"""
Procurement & Sourcing Agent Node.

Evaluates vendor quotations, integrates risk delays, and submits sourcing proposals.
"""

from datetime import datetime
from typing import Any, Dict
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.supplier_tools import evaluate_supplier_proposals


def procurement_sourcing_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    LangGraph node: Solicits bids and ranks supplier proposals.

    Args:
        state (SupplyChainState): Current workflow state containing inventory need and risk data.

    Returns:
        Dict[str, Any]: Partial state update with procurement_proposals and selected_procurement.
    """
    inventory_data = state.get("inventory_analysis", {})
    quantity_needed = inventory_data.get("recommended_reorder_qty", 1000)

    risk_data = state.get("risk_assessment", {})
    disruptions = risk_data.get("disruptions", [])

    proposals = evaluate_supplier_proposals(
        quantity_needed=quantity_needed,
        disruptions=disruptions,
    )

    # Initial tentative selection: choose the fastest available supplier
    # Note: Compliance Agent will subsequently audit this selection for state regulations!
    tentative_choice = proposals[0] if proposals else None

    proposals_summary = " | ".join(
        f"{p['supplier_name']} ({p['country']}): {p['effective_lead_time_days']}d lead, "
        f"{p['unit_price_eur']}€/u, Total: {p['total_material_cost_eur']:,.0f}€"
        for p in proposals
    )

    reasoning = (
        f"[PROCUREMENT AGENT] Evaluated {len(proposals)} vendor options for {quantity_needed} units. "
        f"Proposals: {proposals_summary}. "
        f"Tentatively proposing: {tentative_choice['supplier_name']} (Lead time: {tentative_choice['effective_lead_time_days']} days, "
        f"Cost: {tentative_choice['total_material_cost_eur']:,.2f} EUR). Forwarding to State Compliance Agent."
    )

    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] 🤝 PROCUREMENT_AGENT: "
        f"Ranked {len(proposals)} bids for {quantity_needed} units. "
        f"Top candidate: {tentative_choice['supplier_name']} ({tentative_choice['total_material_cost_eur']:,.2f} EUR)."
    )

    message = {
        "sender": "Procurement_Sourcing_Agent",
        "content": reasoning,
    }

    return {
        "procurement_proposals": proposals,
        "selected_procurement": tentative_choice,
        "current_step": "PROCUREMENT_QUOTED",
        "agent_logs": [log_entry],
        "messages": [message],
    }
