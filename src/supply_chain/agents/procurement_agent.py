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
from src.supply_chain.tools.procurement_tools import evaluate_supplier_proposals_tool
from src.supply_chain.prompts import PROCUREMENT_AGENT_PROMPT
from src.supply_chain.agents.agent_factory import build_react_agent

def procurement_sourcing_node(state: SupplyChainState) -> Dict[str, Any]:
    inventory_data = state.get("inventory_analysis", {})
    required_qty = inventory_data.get("recommended_reorder_qty", 500)
    
    risk_data = state.get("geopolitical_risk", {})
    supplier_delay = risk_data.get("expected_delay_days", 0)

    context = f"\n\nContext:\nRequired Quantity: {required_qty}\nRisk Delays: +{supplier_delay} days"
    system_msg = SystemMessage(content=PROCUREMENT_AGENT_PROMPT + context)
    
    agent = build_react_agent([evaluate_supplier_proposals_tool])
    result = agent.invoke({"messages": [system_msg] + state.get("messages", [])})
    
    proposals = []
    for msg in result["messages"]:
        if isinstance(msg, ToolMessage) and msg.name == "evaluate_supplier_proposals_tool":
            try:
                proposals = json.loads(msg.content)
            except json.JSONDecodeError:
                pass

    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 🤝 PROCUREMENT_AGENT: Sourcing completed."
    if proposals:
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 🤝 PROCUREMENT_AGENT: Evaluated {len(proposals)} proposals. Selected lowest viable bid."

    new_messages = result["messages"][len(state.get("messages", [])) + 1:] 
    
    selected = proposals[0] if proposals else None

    return {
        "procurement_proposals": proposals,
        "selected_procurement": selected,
        "current_step": "PROCUREMENT_SOURCING_COMPLETED",
        "agent_logs": [log_entry],
        "messages": new_messages,
    }
