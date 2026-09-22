"""
Procurement & Sourcing Agent Node.

Official LangChain & LangGraph implementation:
- Uses `llm.bind_tools([evaluate_supplier_proposals_tool])`
- Invokes model with state messages
- Evaluates supplier bids and emits AIMessage with tool calls
"""

import json
from datetime import datetime
from typing import Any, Dict
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.supplier_tools import evaluate_supplier_proposals_tool
from src.supply_chain.prompts import PROCUREMENT_AGENT_PROMPT
from src.supply_chain.llm import get_agent_llm

def procurement_sourcing_node(state: SupplyChainState) -> Dict[str, Any]:
    inventory_data = state.get("inventory_analysis", {})
    quantity_needed = inventory_data.get("recommended_reorder_qty", 1000)
    risk_data = state.get("risk_assessment", {})
    disruptions = risk_data.get("disruptions", [])

    model = get_agent_llm(temperature=0.0).bind_tools([evaluate_supplier_proposals_tool])
    
    context = f"\n\nContext:\nQuantity Needed: {quantity_needed}\nActive Disruptions: {json.dumps(disruptions)}"
    system_msg = SystemMessage(content=PROCUREMENT_AGENT_PROMPT + context)
    messages = [system_msg] + state.get("messages", [])
    
    ai_response = model.invoke(messages)
    proposals = []
    tentative_choice = None
    tool_messages = []
    log_entry = ""
    messages_to_add = [ai_response]

    if hasattr(ai_response, "tool_calls") and ai_response.tool_calls:
        for tool_call in ai_response.tool_calls:
            if tool_call["name"] == "evaluate_supplier_proposals_tool":
                args = tool_call["args"]
                if "quantity_needed" not in args:
                    args["quantity_needed"] = quantity_needed
                if "disruptions" not in args:
                    args["disruptions"] = disruptions
                
                proposals = evaluate_supplier_proposals_tool.invoke(args)
                tool_msg = ToolMessage(
                    content=json.dumps(proposals),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"]
                )
                tool_messages.append(tool_msg)

        if tool_messages:
            messages_to_add.extend(tool_messages)
            final_response = model.invoke(messages + messages_to_add)
            messages_to_add.append(AIMessage(content=final_response.content, name="Procurement_Agent"))
            tentative_choice = proposals[0] if proposals else None
            if tentative_choice:
                log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 🤝 PROCUREMENT_AGENT: Ranked {len(proposals)} bids. Top candidate: {tentative_choice['supplier_name']} ({tentative_choice['total_material_cost_eur']:,.2f} EUR)."
            else:
                log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 🤝 PROCUREMENT_AGENT: No valid proposals found."

    if not proposals:
        messages_to_add = [AIMessage(content=ai_response.content, name="Procurement_Agent")]
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 🤝 PROCUREMENT_AGENT: Manual supplier evaluation without tools."

    return {
        "procurement_proposals": proposals,
        "selected_procurement": tentative_choice,
        "current_step": "PROCUREMENT_QUOTED",
        "agent_logs": [log_entry],
        "messages": messages_to_add,
    }
