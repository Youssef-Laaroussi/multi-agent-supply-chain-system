"""
Sovereign Compliance & State Policy Agent Node.

Represents public authority and legal governance. Enforces trade embargos,
statutory strategic reserve floors, and public procurement oversight with veto authority.
"""

from datetime import datetime
from typing import Any, Dict
from src.supply_chain.state import SupplyChainState
from src.supply_chain.guardrails import (
    validate_embargo_sanctions_guardrail,
    validate_procurement_budget_guardrail,
    validate_strategic_reserve_guardrail,
)
from src.supply_chain.config import SystemConfig


def compliance_governance_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    LangGraph node: Audits proposed transactions against state regulations and sovereign rules.

    Args:
        state (SupplyChainState): Current workflow state with tentative procurement selection.

    Returns:
        Dict[str, Any]: State update with compliance review, approved vendor, and guardrail verdicts.
    """
    tentative = state.get("selected_procurement") or {}
    proposals = state.get("procurement_proposals", [])
    inventory_data = state.get("inventory_analysis", {})
    reserve_floor = state.get("strategic_reserve_floor", SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR)

    audit_log = []
    is_compliant = False
    approved_vendor = None
    veto_issued = False

    # 1. Audit tentative vendor against Embargo & Sovereign Origin
    embargo_passed, embargo_msg, embargo_audit = validate_embargo_sanctions_guardrail(
        supplier_country=tentative.get("country", "UNKNOWN"),
        certified_by_state=tentative.get("certified_by_state", False),
    )
    audit_log.append(embargo_msg)

    if not embargo_passed:
        veto_issued = True
        audit_log.append(
            f"🏛️ VETO EXERCISED: Tentative vendor '{tentative.get('supplier_name')}' rejected by State Compliance. "
            f"Scanning alternative certified sovereign suppliers..."
        )

        # Re-scan proposals for a 100% compliant sovereign supplier
        for candidate in proposals:
            c_passed, _, _ = validate_embargo_sanctions_guardrail(
                supplier_country=candidate.get("country", ""),
                certified_by_state=candidate.get("certified_by_state", False),
            )
            if c_passed:
                approved_vendor = candidate
                audit_log.append(
                    f"✅ APPROVED ALTERNATIVE: Selected '{approved_vendor['supplier_name']}' "
                    f"(Country: {approved_vendor['country']}, State Certified: Yes)."
                )
                break
    else:
        approved_vendor = tentative

    if approved_vendor:
        # 2. Audit Budget Guardrail
        material_cost = approved_vendor.get("total_material_cost_eur", 0.0)
        estimated_freight = approved_vendor.get("quantity_quoted", 0) * 15.0  # Air express estimate

        budget_passed, budget_msg, budget_audit = validate_procurement_budget_guardrail(
            material_cost_eur=material_cost,
            freight_cost_eur=estimated_freight,
            is_emergency_declared=inventory_data.get("strategic_reserve_breach", False),
        )
        audit_log.append(budget_msg)

        # 3. Audit Strategic Reserve Protection
        reserve_passed, reserve_msg, reserve_audit = validate_strategic_reserve_guardrail(
            current_stock=state.get("current_inventory", 750),
            projected_outflow=inventory_data.get("lead_time_demand", 720),
            replenishment_incoming=approved_vendor.get("quantity_quoted", 0),
            reserve_floor=reserve_floor,
        )
        audit_log.append(reserve_msg)

        is_compliant = budget_passed and reserve_passed

    compliance_summary = {
        "status": "APPROVED" if is_compliant else "REJECTED_BY_COMPLIANCE",
        "veto_exercised": veto_issued,
        "approved_supplier_id": approved_vendor.get("supplier_id") if approved_vendor else None,
        "approved_supplier_name": approved_vendor.get("supplier_name") if approved_vendor else None,
        "sovereign_decree_active": True,
        "audit_trail": audit_log,
    }

    reasoning = (
        f"[COMPLIANCE & STATE AGENT] Statutory audit complete. Status: {compliance_summary['status']}. "
        f"Veto exercised: {veto_issued}. "
        f"Legally authorized vendor: {approved_vendor.get('supplier_name') if approved_vendor else 'NONE'}. "
        f"Audit findings: {' | '.join(audit_log)}"
    )

    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] 🏛️ COMPLIANCE_AGENT: "
        f"Status: {compliance_summary['status']} | Veto: {veto_issued} | "
        f"Authorized: {approved_vendor.get('supplier_name') if approved_vendor else 'NONE'}."
    )

    message = {
        "sender": "Sovereign_Compliance_Agent",
        "content": reasoning,
    }

    return {
        "selected_procurement": approved_vendor,
        "compliance_review": compliance_summary,
        "is_compliant": is_compliant,
        "current_step": "COMPLIANCE_REVIEW_COMPLETED",
        "agent_logs": [log_entry],
        "messages": [message],
    }
