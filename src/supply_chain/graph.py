"""
Official LangGraph StateGraph Architecture for the Sovereign Supply Chain Multi-Agent System.

Built strictly according to official LangGraph documentation:
- Typed state dictionary with `add_messages` reducer
- Specialized agent nodes invoking official `@tool` instances
- First-class Guardrail validation node and conditional edge routing
- In-memory persistence via `langgraph.checkpoint.memory.MemorySaver`
"""

from typing import Literal, Optional, Union
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.base import BaseCheckpointSaver
from src.supply_chain.memory import get_checkpointer

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




def build_supply_chain_graph(
    checkpointer: Optional[Union[bool, BaseCheckpointSaver]] = True,
):
    """
    Constructs and compiles the official LangGraph multi-agent pipeline.

    Args:
        checkpointer: 
            - True: uses the configured checkpointer from src.supply_chain.memory
            - False or None: compiles without state persistence
            - BaseCheckpointSaver instance: explicitly uses the provided checkpointer

    Returns:
        CompiledStateGraph: Ready-to-invoke LangGraph runnable.
    """
    workflow = StateGraph(SupplyChainState)

    # 1. Register specialized agent and guardrail nodes
    workflow.add_node("demand_agent", demand_forecasting_node)
    workflow.add_node("inventory_agent", inventory_optimization_node)
    workflow.add_node("risk_agent", risk_assessment_node)
    workflow.add_node("procurement_agent", procurement_sourcing_node)
    workflow.add_node("compliance_guardrail", compliance_governance_node)
    workflow.add_node("logistics_agent", logistics_orchestration_node)
    workflow.add_node("orchestrator_agent", orchestrator_control_tower_node)

    # 2. Add sequential edges across planning & sourcing phases
    workflow.add_edge(START, "demand_agent")
    workflow.add_edge("demand_agent", "inventory_agent")
    workflow.add_edge("inventory_agent", "risk_agent")
    workflow.add_edge("risk_agent", "procurement_agent")
    workflow.add_edge("procurement_agent", "compliance_guardrail")

    # 3. Routing is handled internally by compliance_guardrail via Command API

    # 4. Final edges to Orchestrator and terminal node
    workflow.add_edge("logistics_agent", "orchestrator_agent")
    workflow.add_edge("orchestrator_agent", END)

    # 5. Resolve LangGraph Checkpointer
    active_checkpointer = None
    if isinstance(checkpointer, BaseCheckpointSaver):
        active_checkpointer = checkpointer
    elif checkpointer is True:
        active_checkpointer = get_checkpointer()

    return workflow.compile(checkpointer=active_checkpointer)



# Pre-compiled application instance
supply_chain_app = build_supply_chain_graph(checkpointer=True)
