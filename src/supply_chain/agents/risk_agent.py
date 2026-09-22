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
from src.supply_chain.tools.risk_radar_tools import query_risk_radar_tool
from src.supply_chain.prompts import RISK_AGENT_PROMPT
from src.supply_chain.llm import get_agent_llm

def risk_assessment_node(state: SupplyChainState) -> Dict[str, Any]:
    sku = state.get("sku", "SKU-MED-901")
    model = get_agent_llm(temperature=0.0).bind_tools([query_risk_radar_tool])
    
    context = f"\n\nContext:\nTarget SKU: {sku}"
    system_msg = SystemMessage(content=RISK_AGENT_PROMPT + context)
    messages = [system_msg] + state.get("messages", [])
    
    ai_response = model.invoke(messages)
    risk_data = {}
    tool_messages = []
    log_entry = ""
    messages_to_add = [ai_response]

    if hasattr(ai_response, "tool_calls") and ai_response.tool_calls:
        for tool_call in ai_response.tool_calls:
            if tool_call["name"] == "query_risk_radar_tool":
                args = tool_call["args"]
                if "sku" not in args:
                    args["sku"] = sku
                
                risk_data = query_risk_radar_tool.invoke(args)
                tool_msg = ToolMessage(
                    content=json.dumps(risk_data),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"]
                )
                tool_messages.append(tool_msg)

        if tool_messages:
            messages_to_add.extend(tool_messages)
            final_response = model.invoke(messages + messages_to_add)
            messages_to_add.append(AIMessage(content=final_response.content, name="Risk_Radar_Agent"))
            level = risk_data.get('risk_level', 'UNKNOWN')
            index = risk_data.get('overall_risk_index', 0.0)
            alerts = risk_data.get('active_alerts_count', 0)
            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ RISK_AGENT: Risk Level: {level} (Index: {index}) | {alerts} alerts active."

    if not risk_data:
        messages_to_add = [AIMessage(content=ai_response.content, name="Risk_Radar_Agent")]
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ RISK_AGENT: Manual risk assessment without tools."

    return {
        "risk_assessment": risk_data,
        "current_step": "RISK_ASSESSMENT_COMPLETED",
        "agent_logs": [log_entry],
        "messages": messages_to_add,
    }
