"""
Official State definitions for the LangGraph Multi-Agent Supply Chain System.

Adheres directly to LangGraph docs:
- `Annotated[list[BaseMessage], add_messages]` for multi-agent message channels.
- Typed dictionary (`TypedDict`) for state graph nodes and conditional edge evaluations.
- Pydantic models for structured output validation.
"""

from typing import Annotated, Any, Dict, List, Optional
import operator
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class SupplyChainState(TypedDict):
    """
    Central shared state object traversing the LangGraph state graph.
    Complies with official LangGraph documentation.
    """
    # Strategic item context
    sku: str
    sku_description: str
    current_inventory: int
    strategic_reserve_floor: int

    # Domain outputs produced by specialized agent nodes
    demand_forecast: Dict[str, Any]
    inventory_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    procurement_proposals: List[Dict[str, Any]]
    selected_procurement: Optional[Dict[str, Any]]
    compliance_review: Dict[str, Any]
    logistics_plan: Dict[str, Any]
    orchestrator_decision: Dict[str, Any]

    # Official LangGraph message reducer pattern
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Audit log accumulator
    agent_logs: Annotated[List[str], operator.add]

    # Workflow routing and governance flags
    current_step: str
    is_compliant: bool
    is_completed: bool
