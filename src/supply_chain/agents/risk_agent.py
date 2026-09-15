"""
Risk & Disruption Radar Agent Node.

Monitors external threats, transit corridor bottlenecks, and vendor vulnerabilities.
"""

from datetime import datetime
from typing import Any, Dict
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.risk_radar_tools import query_risk_radar


def risk_assessment_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    LangGraph node: Evaluates external risk environment affecting the supply chain.

    Args:
        state (SupplyChainState): Current workflow state.

    Returns:
        Dict[str, Any]: Partial state update with risk_assessment.
    """
    sku = state.get("sku", "SKU-MED-901")
    risk_data = query_risk_radar(sku)

    alerts_summary = "; ".join(
        f"[{d['type']}] {d['description']} (Delay: +{d['induced_delay_days']}d on {d['impacted_supplier_id']})"
        for d in risk_data["disruptions"]
    )

    reasoning = (
        f"[RISK RADAR AGENT] Global threat index: {risk_data['overall_risk_index']} ({risk_data['risk_level']}). "
        f"Active disruptions detected ({risk_data['active_alerts_count']}): {alerts_summary}."
    )

    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ RISK_AGENT: "
        f"Risk Level: {risk_data['risk_level']} (Index: {risk_data['overall_risk_index']}) | "
        f"{risk_data['active_alerts_count']} alerts active."
    )

    message = {
        "sender": "Risk_Disruption_Agent",
        "content": reasoning,
    }

    return {
        "risk_assessment": risk_data,
        "current_step": "RISK_ASSESSMENT_COMPLETED",
        "agent_logs": [log_entry],
        "messages": [message],
    }
