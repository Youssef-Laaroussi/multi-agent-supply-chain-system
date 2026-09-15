"""
Official LangGraph StateGraph Architecture for the Sovereign Supply Chain Multi-Agent System.

Built strictly according to official LangGraph documentation:
- Typed state dictionary with `add_messages` reducer
- Specialized agent nodes invoking official `@tool` instances
- First-class Guardrail validation node and conditional edge routing
- In-memory persistence via `langgraph.checkpoint.memory.MemorySaver`
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
from src.supply_chain.guardrails.validator_node import sovereign_guardrail_node


def guardrail_conditional_router(
    state: SupplyChainState,
) -> Literal["logistics_agent", "orchestrator_agent"]:
    """
    Official LangGraph conditional edge routing function.

    Evaluates the compliance verdict produced by the guardrail node:
    - If `is_compliant` is True: routes to `logistics_agent` for freight booking.
    - If `is_compliant` is False: routes directly to `orchestrator_agent` for crisis halt decree.
    """
    if state.get("is_compliant", False):
        return "logistics_agent"
    return "orchestrator_agent"


def build_supply_chain_graph(use_checkpointer: bool = True):
    """
    Constructs and compiles the official LangGraph multi-agent pipeline.

    Args:
        use_checkpointer (bool): Enables MemorySaver checkpointer for state persistence.

    Returns:
        CompiledStateGraph: Ready-to-invoke LangGraph runnable.
    """
    workflow = StateGraph(SupplyChainState)

    # 1. Register specialized agent and guardrail nodes
    workflow.add_node("demand_agent", demand_forecasting_node)
    workflow.add_node("inventory_agent", inventory_optimization_node)
    workflow.add_node("risk_agent", risk_assessment_node)
    workflow.add_node("procurement_agent", procurement_sourcing_node)
    workflow.add_node("compliance_guardrail", sovereign_guardrail_node)
    workflow.add_node("logistics_agent", logistics_orchestration_node)
    workflow.add_node("orchestrator_agent", orchestrator_control_tower_node)

    # 2. Add sequential edges across planning & sourcing phases
    workflow.add_edge(START, "demand_agent")
    workflow.add_edge("demand_agent", "inventory_agent")
    workflow.add_edge("inventory_agent", "risk_agent")
    workflow.add_edge("risk_agent", "procurement_agent")
    workflow.add_edge("procurement_agent", "compliance_guardrail")

    # 3. Add conditional edge after guardrail evaluation
    workflow.add_conditional_edges(
        "compliance_guardrail",
        guardrail_conditional_router,
        {
            "logistics_agent": "logistics_agent",
            "orchestrator_agent": "orchestrator_agent",
        },
    )

    # 4. Final edges to Orchestrator and terminal node
    workflow.add_edge("logistics_agent", "orchestrator_agent")
    workflow.add_edge("orchestrator_agent", END)

    # 5. Attach LangGraph Checkpointer (Memory)
    checkpointer = MemorySaver() if use_checkpointer else None
    return workflow.compile(checkpointer=checkpointer)


# Pre-compiled application instance
supply_chain_app = build_supply_chain_graph(use_checkpointer=True)
