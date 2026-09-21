"""
Demand Forecasting Agent Node.

Official LangChain & LangGraph implementation:
- Uses `llm.bind_tools([calculate_demand_forecast_tool])`
- Invokes model with messages history
- Executes tool invocation and returns official AIMessage
"""

import json
from datetime import datetime
from typing import Any, Dict
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from src.supply_chain.state import SupplyChainState
from src.supply_chain.tools.forecasting_tools import calculate_demand_forecast_tool
from src.supply_chain.prompts import DEMAND_AGENT_PROMPT
from src.supply_chain.llm import get_agent_llm

def demand_forecasting_node(state: SupplyChainState) -> Dict[str, Any]:
    sku = state.get("sku", "SKU-MED-901")
    model = get_agent_llm(temperature=0.0).bind_tools([calculate_demand_forecast_tool])
    
    context = f"\n\nContext:\nTarget SKU: {sku}\nHistorical Consumption for reference: [120, 115, 130, 125, 140, 110, 135]"
    system_msg = SystemMessage(content=DEMAND_AGENT_PROMPT + context)
    messages = [system_msg] + state.get("messages", [])
    
    ai_response = model.invoke(messages)
    forecast_data = {}
    tool_messages = []
    log_entry = ""
    messages_to_add = [ai_response]
    
    if hasattr(ai_response, "tool_calls") and ai_response.tool_calls:
        for tool_call in ai_response.tool_calls:
            if tool_call["name"] == "calculate_demand_forecast_tool":
                args = tool_call["args"]
                if "sku" not in args:
                    args["sku"] = sku
                if "historical_consumption" not in args or not args["historical_consumption"]:
                    args["historical_consumption"] = [120, 115, 130, 125, 140, 110, 135]
                
                forecast_data = calculate_demand_forecast_tool.invoke(args)
                tool_msg = ToolMessage(
                    content=json.dumps(forecast_data),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"]
                )
                tool_messages.append(tool_msg)
                
        if tool_messages:
            messages_to_add.extend(tool_messages)
            final_response = model.invoke(messages + messages_to_add)
            messages_to_add.append(AIMessage(content=final_response.content, name="Demand_Forecasting_Agent"))
            surge = forecast_data.get('surge_percentage', '0%')
            total = forecast_data.get('total_projected_demand', 0)
            log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 📈 DEMAND_AGENT: Surge detected (+{surge}). Total 7-day demand: {total} units."
    
    if not forecast_data:
        messages_to_add = [AIMessage(content=ai_response.content, name="Demand_Forecasting_Agent")]
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 📈 DEMAND_AGENT: Manual forecast estimation without tools."

    return {
        "demand_forecast": forecast_data,
        "current_step": "DEMAND_FORECAST_COMPLETED",
        "agent_logs": [log_entry],
        "messages": messages_to_add,
    }
