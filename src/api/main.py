import json
import asyncio
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from src.supply_chain.graph import supply_chain_app
from src.supply_chain.config import SystemConfig, SUPPLIER_CATALOG, CARRIER_CATALOG

app = FastAPI(title="Sovereign Supply Chain API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Returns API health status, LangGraph engine metadata, and statutory parameters."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "engine": "LangGraph v1.0 StateGraph + ToolNode + Command",
        "checkpointer": "MemorySaver (Active)",
        "strategic_reserve_floor": SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR,
        "spending_ceiling_eur": SystemConfig.MAX_EXPRESS_PURCHASE_BUDGET_EUR,
    }


@app.get("/api/catalogs")
async def get_catalogs():
    """Returns system catalogs: strategic SKUs, suppliers, carriers, and guardrail thresholds."""
    return {
        "strategic_skus": list(SystemConfig.STRATEGIC_SKUS),
        "reserve_floor": SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR,
        "spending_ceiling_eur": SystemConfig.MAX_EXPRESS_PURCHASE_BUDGET_EUR,
        "emergency_ceiling_eur": SystemConfig.EMERGENCY_BUDGET_CEILING_EUR,
        "sanctioned_countries": list(SystemConfig.SANCTIONED_COUNTRIES),
        "suppliers": SUPPLIER_CATALOG,
        "carriers": CARRIER_CATALOG,
    }


@app.get("/api/graph")
async def get_graph_topology():
    """Returns the live Mermaid diagram generated directly by LangGraph's StateGraph."""
    return {
        "mermaid": supply_chain_app.get_graph().draw_mermaid(),
        "nodes": list(supply_chain_app.get_graph().nodes.keys()),
    }


class SimulationRequest(BaseModel):
    sku: str = "SKU-MED-901"
    starting_stock: int = 750
    prompt: str = ""


@app.post("/api/simulate")
async def start_simulation(request: SimulationRequest):
    """Streams LangGraph execution updates via Server-Sent Events (SSE) with MemorySaver checkpointing."""
    async def event_generator():
        thread_id = f"crisis-thread-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        config = {"configurable": {"thread_id": thread_id}}

        initial_messages = [HumanMessage(content=request.prompt)] if request.prompt else []
        initial_state = {
            "sku": request.sku,
            "sku_description": "Emergency Strategic Supplies & Critical Infrastructure",
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

        await asyncio.sleep(0.3)

        for event in supply_chain_app.stream(initial_state, config=config, stream_mode="updates"):
            for node_name, node_output in event.items():
                if not isinstance(node_output, dict):
                    continue
                node_logs = node_output.get("agent_logs", [])
                node_messages = node_output.get("messages", [])
                latest_msg = ""
                if node_logs:
                    latest_msg = node_logs[-1]
                elif node_messages:
                    last_msg = node_messages[-1]
                    latest_msg = getattr(last_msg, "content", str(last_msg))

                payload = {
                    "thread_id": thread_id,
                    "node": node_name,
                    "message": latest_msg,
                    "state_update": {
                        k: v for k, v in node_output.items() if k not in ["messages", "agent_logs"]
                    },
                }
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.6)

        yield f"data: {json.dumps({'node': 'END', 'thread_id': thread_id, 'message': 'Simulation completed and checkpointed.'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
