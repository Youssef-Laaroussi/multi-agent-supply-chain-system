"""
Risk & Disruption Radar Agent Node.

Official LangChain & LangGraph implementation:
- Uses `llm.bind_tools([query_risk_radar_tool])`
- Invokes model with state messages
- Returns AIMessage with disruption details and tool calls
"""

from datetime import datetime
from typing import Any, Dict
from langchain_core.messages import AIMessage, SystemMessage
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.risk_radar_tools import query_risk_radar_tool
from src.supply_chain.prompts import RISK_AGENT_PROMPT
from src.supply_chain.llm import get_agent_llm


def risk_assessment_node(state: SupplyChainState) -> Dict[str, Any]:
    """
    LangGraph agent node: Monitors external environmental and transit risks.
    """
    sku = state.get("sku", "SKU-MED-901")

    # 1. Official tool binding and model invocation
    model = get_agent_llm(temperature=0.0).bind_tools([query_risk_radar_tool])
    system_msg = SystemMessage(content=RISK_AGENT_PROMPT)
    ai_response = model.invoke([system_msg] + state.get("messages", []))

    # 2. Execute tool invocation
    risk_data = query_risk_radar_tool.invoke({"sku": sku})

    alerts_summary = "; ".join(
        f"[{d['type']}] {d['description']} (Delay: +{d['induced_delay_days']}d on {d['impacted_supplier_id']})"
        for d in risk_data["disruptions"]
    )

    reasoning = (
        f"[RISK RADAR AGENT] Global threat index: {risk_data['overall_risk_index']} ({risk_data['risk_level']}). "
        f"Active disruptions detected ({risk_data['active_alerts_count']}): {alerts_summary}."
    )

    ai_msg = AIMessage(
        content=reasoning,
        name="Risk_Disruption_Agent",
        tool_calls=ai_response.tool_calls,
    )
    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ RISK_AGENT: "
        f"Risk Level: {risk_data['risk_level']} (Index: {risk_data['overall_risk_index']}) | "
        f"{risk_data['active_alerts_count']} alerts active."
    )

    return {
        "risk_assessment": risk_data,
        "current_step": "RISK_ASSESSMENT_COMPLETED",
        "agent_logs": [log_entry],
        "messages": [ai_msg],
    }
