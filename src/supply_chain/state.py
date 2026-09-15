"""
State definitions for the LangGraph Multi-Agent Supply Chain System.

This module defines the typed state schema (`SupplyChainState`) flowing through all
LangGraph agent nodes. It maintains full auditability, agent communication history,
and state variables across the entire supply chain workflow.
"""

from typing import Annotated, Any, Dict, List, Optional
import operator
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


class AgentLogEntry(BaseModel):
    """Structured audit log entry emitted by an agent."""
    agent_name: str = Field(..., description="Name of the reporting agent")
    timestamp: str = Field(..., description="ISO formatted timestamp")
    action: str = Field(..., description="Action taken or decision made")
    details: Dict[str, Any] = Field(default_factory=dict, description="Structured metadata")


class SupplyChainState(TypedDict):
    """
    Central shared state object traversing the LangGraph state graph.
    
    Attributes:
        sku (str): Strategic item identifier being evaluated.
        sku_description (str): Human-readable name/description of the item.
        current_inventory (int): Current available warehouse stock level.
        strategic_reserve_floor (int): Minimum required state strategic stock.
        
        # Agent outputs
        demand_forecast (Dict[str, Any]): Produced by Demand Forecasting Agent.
        inventory_analysis (Dict[str, Any]): Produced by Inventory Optimization Agent.
        risk_assessment (Dict[str, Any]): Produced by Risk & Disruption Agent.
        procurement_proposals (List[Dict[str, Any]]): Sourced by Procurement Agent.
        selected_procurement (Optional[Dict[str, Any]]): Tentatively selected quote.
        compliance_review (Dict[str, Any]): Produced by Sovereign Compliance Agent.
        logistics_plan (Dict[str, Any]): Produced by Logistics & Fleet Agent.
        orchestrator_decision (Dict[str, Any]): Master synthesis & arbitration.
        
        # Memory & Audit Trails
        agent_logs: Annotated[List[str], operator.add]
        messages: Annotated[List[Dict[str, str]], operator.add]
        
        # Workflow control
        current_step (str): Current execution checkpoint.
        is_compliant (bool): True if State Compliance passed without veto.
        is_completed (bool): True if orchestration workflow concluded.
    """
    sku: str
    sku_description: str
    current_inventory: int
    strategic_reserve_floor: int

    demand_forecast: Dict[str, Any]
    inventory_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    procurement_proposals: List[Dict[str, Any]]
    selected_procurement: Optional[Dict[str, Any]]
    compliance_review: Dict[str, Any]
    logistics_plan: Dict[str, Any]
    orchestrator_decision: Dict[str, Any]

    agent_logs: Annotated[List[str], operator.add]
    messages: Annotated[List[Dict[str, str]], operator.add]

    current_step: str
    is_compliant: bool
    is_completed: bool
