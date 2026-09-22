"""
Master Orchestrator Agent Node (Supply Chain Control Tower).

Synthesizes recommendations across all specialist agents, balances trade-offs,
and issues the binding Executive Supply Order.
Adheres to official LangChain & LangGraph standards with BaseMessage history.
"""

import json
from datetime import datetime
from typing import Any, Dict
from langchain_core.messages import AIMessage, SystemMessage
from src.supply_chain.state import SupplyChainState
from src.supply_chain.prompts import ORCHESTRATOR_PROMPT
from src.supply_chain.llm import get_agent_llm

def orchestrator_control_tower_node(state: SupplyChainState) -> Dict[str, Any]:
    sku = state.get("sku", "SKU-MED-901")
    procurement = state.get("selected_procurement") or {}
    compliance = state.get("compliance_review", {})
    logistics = state.get("logistics_plan", {})

    material_cost = procurement.get("total_material_cost_eur", 0.0)
    freight_cost = logistics.get("total_freight_cost_eur", 0.0)
    total_investment_eur = material_cost + freight_cost

    supplier_lead = procurement.get("effective_lead_time_days", 2)
    transit_days = logistics.get("transit_days", 1)
    total_cycle_time_days = supplier_lead + transit_days

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
    }

    model = get_agent_llm(temperature=0.0)
    context = f"\n\nContext:\nDecision Summary: {json.dumps(decision_summary, indent=2)}\nState Audit Logs: {state.get('agent_logs', [])}"
    system_msg = SystemMessage(content=ORCHESTRATOR_PROMPT + context)
    messages = [system_msg] + state.get("messages", [])
    
    ai_response = model.invoke(messages)
    decision_summary["trade_off_resolution"] = ai_response.content
    
    reasoning = (
        f"[MASTER ORCHESTRATOR] 🎯 EXECUTIVE VERDICT: {decision_summary['verdict']}. "
        f"Order {decision_summary['executive_order_id']} issued for {decision_summary['units_ordered']} units of {sku}. "
        f"Supplier: {decision_summary['authorized_supplier']} | Carrier: {decision_summary['carrier_assigned']} | "
        f"Total Cycle Time: {total_cycle_time_days} days | Total Budget: {total_investment_eur:,.2f} EUR. "
        f"Trade-off Resolution:\n{decision_summary['trade_off_resolution']}"
    )

    ai_message = AIMessage(content=reasoning, name="Master_Orchestrator_Agent")
    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] 👑 ORCHESTRATOR: "
        f"Verdict: {decision_summary['verdict']} | Order: {decision_summary['executive_order_id']} | "
        f"Total: {total_investment_eur:,.2f} EUR | ETA: {total_cycle_time_days}d."
    )

    return {
        "orchestrator_decision": decision_summary,
        "is_completed": True,
        "current_step": "ORCHESTRATION_FINALIZED",
        "agent_logs": [log_entry],
        "messages": [ai_message],
    }
