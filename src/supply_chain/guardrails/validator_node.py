"""
Official LangGraph Guardrail Validator Node.

Following LangGraph architectural patterns:
- Intercepts state transitions
- Enforces strict Pydantic and state invariants (Sanctions, Strategic Reserves, Budget Limits)
- Emits structured LangChain messages with guardrail verdicts
- Determines conditional routing via graph edges
"""

from datetime import datetime
from typing import Any, Dict
from langchain_core.messages import AIMessage
from src.supply_chain.state import SupplyChainState
from src.supply_chain.guardrails.embargo_sanction_guardrail import validate_embargo_sanctions_guardrail
from src.supply_chain.guardrails.procurement_budget_guardrail import validate_procurement_budget_guardrail
from src.supply_chain.guardrails.strategic_reserve_guardrail import validate_strategic_reserve_guardrail
from src.supply_chain.config import SystemConfig


def sovereign_guardrail_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    LangGraph Guardrail Node: Evaluates all state invariants before downstream operations.

    Args:
        state (SupplyChainState): State containing tentative supplier and inventory need.

    Returns:
        Dict[str, Any]: Partial state update with guardrail verdict and audit message.
    """
    tentative = state.get("selected_procurement") or {}
    proposals = state.get("procurement_proposals", [])
    inventory_data = state.get("inventory_analysis", {})
    reserve_floor = state.get("strategic_reserve_floor", SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR)

    audit_findings = []
    is_compliant = False
    approved_vendor = None
    veto_issued = False

    # 1. Embargo & Sovereign Origin Guardrail
    embargo_passed, embargo_msg, _ = validate_embargo_sanctions_guardrail(
        supplier_country=tentative.get("country", "UNKNOWN"),
        certified_by_state=tentative.get("certified_by_state", False),
    )
    audit_findings.append(embargo_msg)

    if not embargo_passed:
        veto_issued = True
        audit_findings.append(
            f"VETO EXERCISED: Vendor '{tentative.get('supplier_name')}' blocked by Embargo Guardrail. "
            f"Scanning compliant alternatives..."
        )
        for candidate in proposals:
            c_passed, _, _ = validate_embargo_sanctions_guardrail(
                supplier_country=candidate.get("country", ""),
                certified_by_state=candidate.get("certified_by_state", False),
            )
            if c_passed:
                approved_vendor = candidate
                audit_findings.append(f"ALTERNATIVE APPROVED: '{approved_vendor['supplier_name']}' is certified.")
                break
    else:
        approved_vendor = tentative

    if approved_vendor:
        # 2. Public Budget Guardrail
        material_cost = approved_vendor.get("total_material_cost_eur", 0.0)
        estimated_freight = approved_vendor.get("quantity_quoted", 0) * 15.0
        budget_passed, budget_msg, _ = validate_procurement_budget_guardrail(
            material_cost_eur=material_cost,
            freight_cost_eur=estimated_freight,
            is_emergency_declared=inventory_data.get("strategic_reserve_breach", False),
        )
        audit_findings.append(budget_msg)

        # 3. Strategic Reserve Protection Guardrail
        reserve_passed, reserve_msg, _ = validate_strategic_reserve_guardrail(
            current_stock=state.get("current_inventory", 750),
            projected_outflow=inventory_data.get("lead_time_demand", 720),
            replenishment_incoming=approved_vendor.get("quantity_quoted", 0),
            reserve_floor=reserve_floor,
        )
        audit_findings.append(reserve_msg)

        is_compliant = budget_passed and reserve_passed

    guardrail_verdict = "PASSED" if is_compliant else "VETOED"
    reasoning = (
        f"[LANGGRAPH GUARDRAIL] Status: {guardrail_verdict}. Veto issued: {veto_issued}. "
        f"Approved supplier: {approved_vendor.get('supplier_name') if approved_vendor else 'NONE'}. "
        f"Audit: {' | '.join(audit_findings)}"
    )

    ai_msg = AIMessage(content=reasoning, name="Sovereign_Guardrail_Validator")
    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] 🛡️ GUARDRAIL: "
        f"Verdict: {guardrail_verdict} | Veto: {veto_issued} | "
        f"Authorized: {approved_vendor.get('supplier_name') if approved_vendor else 'NONE'}."
    )

    compliance_summary = {
        "status": "APPROVED" if is_compliant else "REJECTED_BY_COMPLIANCE",
        "guardrail_verdict": guardrail_verdict,
        "veto_exercised": veto_issued,
        "approved_supplier_id": approved_vendor.get("supplier_id") if approved_vendor else None,
        "approved_supplier_name": approved_vendor.get("supplier_name") if approved_vendor else None,
        "audit_trail": audit_findings,
    }

    return {
        "selected_procurement": approved_vendor,
        "compliance_review": compliance_summary,
        "is_compliant": is_compliant,
        "current_step": "GUARDRAIL_EVALUATED",
        "messages": [ai_msg],
        "agent_logs": [log_entry],
    }
