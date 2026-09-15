"""
Risk & Disruption Radar Agent Node.

Adheres to LangChain & LangGraph standards:
- Invokes official `@tool` (`query_risk_radar_tool`)
- Synthesizes risk environment via LangChain ChatModel (`get_agent_llm`)
- Returns official `AIMessage` instances
"""

from datetime import datetime
from typing import Any, Dict
from langchain_core.messages import AIMessage
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.risk_radar_tools import query_risk_radar_tool


def risk_assessment_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    LangGraph node: Evaluates external risk environment affecting the supply chain.

    Args:
        state (SupplyChainState): Current workflow state.

    Returns:
        Dict[str, Any]: Partial state update with risk_assessment and AIMessage.
    """
    sku = state.get("sku", "SKU-MED-901")
    
    # 1. Invoke official LangChain BaseTool
    risk_data = query_risk_radar_tool.invoke({"sku": sku})

    alerts_summary = "; ".join(
        f"[{d['type']}] {d['description']} (Delay: +{d['induced_delay_days']}d on {d['impacted_supplier_id']})"
        for d in risk_data["disruptions"]
    )

    reasoning = (
        f"[RISK RADAR AGENT] Global threat index: {risk_data['overall_risk_index']} ({risk_data['risk_level']}). "
        f"Active disruptions detected ({risk_data['active_alerts_count']}): {alerts_summary}."
    )

    ai_message = AIMessage(content=reasoning, name="Risk_Disruption_Agent")
    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ RISK_AGENT: "
        f"Risk Level: {risk_data['risk_level']} (Index: {risk_data['overall_risk_index']}) | "
        f"{risk_data['active_alerts_count']} alerts active."
    )

    return {
        "risk_assessment": risk_data,
        "current_step": "RISK_ASSESSMENT_COMPLETED",
        "agent_logs": [log_entry],
        "messages": [ai_message],
    }
