"""
LangGraph StateGraph compilation for the Sovereign Supply Chain Multi-Agent System.

Constructs the directed execution graph with:
- 7 specialized agent nodes
- Conditional edge routing (compliance check & veto branch)
- In-memory state persistence via LangGraph Checkpointer (`MemorySaver`)
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.supply_chain.state import SupplyChainState
from src.supply_chain.agents import (
    demand_forecasting_node,
    inventory_optimization_node,
    risk_assessment_node,
    procurement_sourcing_node,
    compliance_governance_node,
    logistics_orchestration_node,
    orchestrator_control_tower_node,
)


def route_after_compliance(
    state: SupplyChainState,
) -> Literal["logistics_agent", "orchestrator_agent"]:
    """
    Conditional edge router evaluating the compliance verdict.

    - If compliant: route to logistics planning.
    - If non-compliant/vetoed: bypass logistics and route to orchestrator for emergency decree.
    """
    if state.get("is_compliant", False):
        return "logistics_agent"
    return "orchestrator_agent"


def build_supply_chain_graph(use_checkpointer: bool = True):
    """
    Constructs and compiles the multi-agent LangGraph workflow.

    Args:
        use_checkpointer (bool): If True, attaches a MemorySaver for checkpoint persistence.

    Returns:
        CompiledStateGraph: Ready-to-invoke LangGraph agent pipeline.
    """
    workflow = StateGraph(SupplyChainState)

    # 1. Register all 7 agent nodes
    workflow.add_node("demand_agent", demand_forecasting_node)
    workflow.add_node("inventory_agent", inventory_optimization_node)
    workflow.add_node("risk_agent", risk_assessment_node)
    workflow.add_node("procurement_agent", procurement_sourcing_node)
    workflow.add_node("compliance_agent", compliance_governance_node)
    workflow.add_node("logistics_agent", logistics_orchestration_node)
    workflow.add_node("orchestrator_agent", orchestrator_control_tower_node)

    # 2. Define deterministic sequential transitions
    workflow.add_edge(START, "demand_agent")
    workflow.add_edge("demand_agent", "inventory_agent")
    workflow.add_edge("inventory_agent", "risk_agent")
    workflow.add_edge("risk_agent", "procurement_agent")
    workflow.add_edge("procurement_agent", "compliance_agent")

    # 3. Add conditional edge for State Compliance & Veto governance
    workflow.add_conditional_edges(
        "compliance_agent",
        route_after_compliance,
        {
            "logistics_agent": "logistics_agent",
            "orchestrator_agent": "orchestrator_agent",
        },
    )

    # 4. Final transitions to Orchestrator and completion
    workflow.add_edge("logistics_agent", "orchestrator_agent")
    workflow.add_edge("orchestrator_agent", END)

    # 5. Compile with optional Memory Checkpointer
    checkpointer = MemorySaver() if use_checkpointer else None
    compiled_app = workflow.compile(checkpointer=checkpointer)
    return compiled_app


# Default pre-compiled graph instance
supply_chain_app = build_supply_chain_graph(use_checkpointer=True)
