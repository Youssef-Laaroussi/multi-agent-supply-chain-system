"""
Risk & Disruption Radar Agent Node.

Official LangChain & LangGraph implementation:
- Uses `llm.bind_tools([query_risk_radar_tool])`
- Invokes model with state messages
- Returns AIMessage with disruption details and tool calls
"""

import json
from datetime import datetime
from typing import Any, Dict
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.risk_tools import monitor_geopolitical_risk_tool
from src.supply_chain.prompts import RISK_AGENT_PROMPT
from src.supply_chain.agents.agent_factory import build_react_agent

def risk_assessment_node(state: SupplyChainState) -> Dict[str, Any]:
    context = f"\n\nContext:\nOrigin Country: {state.get('supplier_country', 'Global')}"
    system_msg = SystemMessage(content=RISK_AGENT_PROMPT + context)
    
    agent = build_react_agent([monitor_geopolitical_risk_tool])
    result = agent.invoke({"messages": [system_msg] + state.get("messages", [])})
    
    risk_data = {}
    for msg in result["messages"]:
        if isinstance(msg, ToolMessage) and msg.name == "monitor_geopolitical_risk_tool":
            try:
                risk_data = json.loads(msg.content)
            except json.JSONDecodeError:
                pass

    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 RISK_AGENT: Assessed risks."
    if risk_data:
        delay = risk_data.get('expected_delay_days', 0)
        level = risk_data.get('risk_level', 'LOW')
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 RISK_AGENT: Level: {level} | Delay impact: +{delay} days."

    new_messages = result["messages"][len(state.get("messages", [])) + 1:] 
    
    return {
        "geopolitical_risk": risk_data,
        "current_step": "RISK_ASSESSMENT_COMPLETED",
        "agent_logs": [log_entry],
        "messages": new_messages,
    }
