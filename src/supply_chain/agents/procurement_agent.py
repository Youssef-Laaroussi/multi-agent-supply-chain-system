"""
Procurement & Sourcing Agent Node.

Official LangChain & LangGraph implementation:
- Uses `llm.bind_tools([evaluate_supplier_proposals_tool])`
- Invokes model with state messages
- Evaluates supplier bids and emits AIMessage with tool calls
"""

from datetime import datetime
from typing import Any, Dict
from langchain_core.messages import AIMessage, SystemMessage
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.supplier_tools import evaluate_supplier_proposals_tool
from src.supply_chain.prompts import PROCUREMENT_AGENT_PROMPT
from src.supply_chain.llm import get_agent_llm


def procurement_sourcing_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    LangGraph agent node: Evaluates supplier proposals and ranks bids.
    """
    inventory_data = state.get("inventory_analysis", {})
    quantity_needed = inventory_data.get("recommended_reorder_qty", 1000)

    risk_data = state.get("risk_assessment", {})
    disruptions = risk_data.get("disruptions", [])

    # 1. Official tool binding and model invocation
    model = get_agent_llm(temperature=0.0).bind_tools([evaluate_supplier_proposals_tool])
    system_msg = SystemMessage(content=PROCUREMENT_AGENT_PROMPT)
    ai_response = model.invoke([system_msg] + state.get("messages", []))

    # 2. Execute tool invocation
    proposals = evaluate_supplier_proposals_tool.invoke({
        "quantity_needed": quantity_needed,
        "disruptions": disruptions,
    })

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
        f"Cost: {tentative_choice['total_material_cost_eur']:,.2f} EUR). Forwarding to Sovereign Guardrail."
    )

    ai_msg = AIMessage(
        content=reasoning,
        name="Procurement_Agent",
    )
    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] 🤝 PROCUREMENT_AGENT: "
        f"Ranked {len(proposals)} bids for {quantity_needed} units. "
        f"Top candidate: {tentative_choice['supplier_name']} ({tentative_choice['total_material_cost_eur']:,.2f} EUR)."
    )

    return {
        "procurement_proposals": proposals,
        "selected_procurement": tentative_choice,
        "current_step": "PROCUREMENT_QUOTED",
        "agent_logs": [log_entry],
        "messages": [ai_msg],
    }
