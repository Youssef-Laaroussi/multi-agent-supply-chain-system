import json
import asyncio
from datetime import datetime
from typing import Any, Dict
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.supply_chain.graph import build_supply_chain_graph
from src.supply_chain.config import SystemConfig

app = FastAPI(title="Sovereign Supply Chain API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationRequest(BaseModel):
    sku: str = "SKU-MED-901"
    starting_stock: int = 750
    prompt: str = ""

@app.post("/api/simulate")
async def start_simulation(request: SimulationRequest):
    """
    Starts the LangGraph simulation and streams the events via Server-Sent Events (SSE).
    """
    async def event_generator():
        graph = build_supply_chain_graph(use_checkpointer=False)
        thread_id = f"crisis-thread-{datetime.now().strftime('%Y%m%d-%H%M')}"
        config = {"configurable": {"thread_id": thread_id}}

        from langchain_core.messages import HumanMessage
        initial_messages = []
        if request.prompt:
            initial_messages.append(HumanMessage(content=request.prompt))

        initial_state = {
            "sku": request.sku,
            "sku_description": "Emergency Strategic Medical Supplies & Intensive Care Filters",
            "current_inventory": request.starting_stock,
            "strategic_reserve_floor": SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR,
            "demand_forecast": {},
            "inventory_analysis": {},
            "risk_assessment": {},
            "procurement_proposals": [],
            "selected_procurement": None,
            "compliance_review": {},
            "logistics_plan": {},
            "orchestrator_decision": {},
            "agent_logs": [],
            "messages": initial_messages,
            "current_step": "INITIALIZED",
            "is_compliant": False,
            "is_completed": False,
        }

        # Small delay to let the UI render the start state
        await asyncio.sleep(0.5)

        for event in graph.stream(initial_state, config=config):
            # event is a dict with node_name as key and node_output as value
            for node_name, node_output in event.items():
                
                # Extract the last message content safely
                node_messages = node_output.get("messages", [])
                latest_msg = ""
                if node_messages:
                    last_msg = node_messages[-1]
                    latest_msg = getattr(last_msg, "content", str(last_msg))
                
                payload = {
                    "node": node_name,
                    "message": latest_msg,
                    "state_update": {k: v for k, v in node_output.items() if k not in ["messages", "agent_logs"]}
                }
                
                # Send Server-Sent Event
                yield f"data: {json.dumps(payload)}\n\n"
                
                # Small sleep to simulate processing and make UI animations visible
                await asyncio.sleep(1.0)

        yield f"data: {json.dumps({'node': 'END', 'message': 'Simulation completed successfully.'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
