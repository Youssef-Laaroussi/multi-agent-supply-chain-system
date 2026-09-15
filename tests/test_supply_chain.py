"""
Automated Test Suite for Sovereign Supply Chain Multi-Agent System.

Validates:
- Official LangChain BaseTool instances created with @tool and Pydantic schemas
- Sovereign Guardrails (embargo sanctions, strategic reserves, public budget)
- End-to-end LangGraph StateGraph execution with BaseMessage channels
"""

import pytest
from src.supply_chain.config import SystemConfig
from src.supply_chain.tools import (
    calculate_demand_forecast_tool,
    calculate_inventory_metrics_tool,
    query_risk_radar_tool,
    evaluate_supplier_proposals_tool,
    plan_freight_dispatch_tool,
)
from src.supply_chain.guardrails import (
    validate_strategic_reserve_guardrail,
    validate_procurement_budget_guardrail,
    validate_embargo_sanctions_guardrail,
)
from src.supply_chain.graph import build_supply_chain_graph


# ==============================================================================
# 1. OFFICIAL LANGCHAIN @TOOL TESTS
# ==============================================================================

def test_forecasting_tool_invocation():
    """Verify that the official @tool calculates demand and detects surge anomalies."""
    result = calculate_demand_forecast_tool.invoke({
        "sku": "SKU-MED-901",
        "historical_consumption": [100, 100, 100],
        "growth_multiplier": 1.0,
        "emergency_shock_factor": 0.50,
    })
    assert result["anomaly_detected"] is True
    assert result["surge_percentage"] == "50%"
    assert result["total_projected_demand"] == 1050


def test_inventory_tool_invocation():
    """Verify that the official @tool detects strategic reserve breach correctly."""
    metrics = calculate_inventory_metrics_tool.invoke({
        "current_stock": 600,
        "daily_demand": 100.0,
        "lead_time_days": 3,
        "strategic_reserve_floor": 500,
    })
    assert metrics["strategic_reserve_breach"] is True
    assert metrics["reorder_needed"] is True
    assert metrics["recommended_reorder_qty"] > 0


def test_supplier_tool_invocation():
    """Verify that the supplier @tool integrates risk delay penalties."""
    disruptions = [
        {
            "impacted_supplier_id": "SUP-GLOBAL-02",
            "induced_delay_days": 5,
        }
    ]
    proposals = evaluate_supplier_proposals_tool.invoke({
        "quantity_needed": 500,
        "disruptions": disruptions,
    })
    global_sup = next(p for p in proposals if p["supplier_id"] == "SUP-GLOBAL-02")
    assert global_sup["disruption_delay_days"] == 5
    assert global_sup["effective_lead_time_days"] == global_sup["base_lead_time_days"] + 5


def test_logistics_tool_invocation():
    """Verify that the logistics @tool books express cargo for critical urgency."""
    dispatch = plan_freight_dispatch_tool.invoke({
        "quantity_units": 1000,
        "urgency_level": "CRITICAL",
        "require_security_escort": True,
    })
    assert dispatch["speed_tier"] == "CRITICAL_EXPRESS"
    assert dispatch["security_certified"] is True
    assert dispatch["transit_days"] == 1


# ==============================================================================
# 2. SOVEREIGN GUARDRAILS TESTS
# ==============================================================================

def test_embargo_guardrail_veto():
    """Verify that an embargoed supplier triggers an explicit State VETO."""
    passed, msg, audit = validate_embargo_sanctions_guardrail(
        supplier_country="EMBARGO_LAND",
        certified_by_state=False,
    )
    assert passed is False
    assert "STATE SANCTIONS & EMBARGO LIST" in msg
    assert audit["is_sanctioned"] is True


def test_embargo_guardrail_approved():
    """Verify that a certified sovereign supplier passes origin inspection."""
    passed, msg, _ = validate_embargo_sanctions_guardrail(
        supplier_country="DOMESTIC",
        certified_by_state=True,
    )
    assert passed is True
    assert "accredited and compliant" in msg


def test_procurement_budget_guardrail_emergency_expansion():
    """Verify that declaring an emergency allows the expanded emergency ceiling."""
    passed, msg, audit = validate_procurement_budget_guardrail(
        material_cost_eur=180_000.0,
        freight_cost_eur=20_000.0,
        is_emergency_declared=True,
    )
    assert passed is True
    assert audit["effective_ceiling_eur"] == SystemConfig.EMERGENCY_BUDGET_CEILING_EUR


def test_procurement_budget_guardrail_peacetime_violation():
    """Verify that standard operations reject expenditures exceeding the 100k cap."""
    passed, msg, _ = validate_procurement_budget_guardrail(
        material_cost_eur=120_000.0,
        freight_cost_eur=10_000.0,
        is_emergency_declared=False,
    )
    assert passed is False
    assert "exceeds statutory spending ceiling" in msg


def test_strategic_reserve_guardrail_violation():
    """Verify that drops below the statutory floor trigger a guardrail violation."""
    passed, msg, _ = validate_strategic_reserve_guardrail(
        current_stock=550,
        projected_outflow=200,
        replenishment_incoming=0,
        reserve_floor=500,
    )
    assert passed is False
    assert "breaches statutory reserve floor" in msg


# ==============================================================================
# 3. END-TO-END LANGGRAPH WORKFLOW TEST
# ==============================================================================

def test_full_langgraph_execution():
    """Verify that the compiled LangGraph pipeline executes all nodes to completion."""
    app = build_supply_chain_graph(use_checkpointer=True)
    config = {"configurable": {"thread_id": "unit-test-thread-001"}}

    initial_state = {
        "sku": "SKU-MED-901",
        "sku_description": "Unit Test Medical Supplies",
        "current_inventory": 750,
        "strategic_reserve_floor": 500,
        "demand_forecast": {},
        "inventory_analysis": {},
        "risk_assessment": {},
        "procurement_proposals": [],
        "selected_procurement": None,
        "compliance_review": {},
        "logistics_plan": {},
        "orchestrator_decision": {},
        "agent_logs": [],
        "messages": [],
        "current_step": "INITIALIZED",
        "is_compliant": False,
        "is_completed": False,
    }

    final_state = app.invoke(initial_state, config=config)

    assert final_state["is_completed"] is True
    assert final_state["is_compliant"] is True
    assert final_state["orchestrator_decision"]["verdict"] == "AUTHORIZED_AND_DISPATCHED"
    assert len(final_state["agent_logs"]) >= 6
    assert len(final_state["messages"]) >= 6
