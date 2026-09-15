"""
Automated Test Suite for Sovereign Supply Chain Multi-Agent System.

Tests cover:
- Deterministic tools (forecasting, inventory, supplier, logistics)
- Sovereign Guardrails (embargo sanctions, strategic reserves, public budget)
- End-to-end LangGraph StateGraph execution
"""

import pytest
from src.supply_chain.config import SystemConfig
from src.supply_chain.tools import (
    calculate_demand_forecast,
    calculate_inventory_metrics,
    query_risk_radar,
    evaluate_supplier_proposals,
    plan_freight_dispatch,
)
from src.supply_chain.guardrails import (
    validate_strategic_reserve_guardrail,
    validate_procurement_budget_guardrail,
    validate_embargo_sanctions_guardrail,
)
from src.supply_chain.graph import build_supply_chain_graph


# ==============================================================================
# 1. TOOLS TESTS
# ==============================================================================

def test_forecasting_tool_surge_detection():
    """Verify that forecasting identifies emergency surges correctly."""
    result = calculate_demand_forecast(
        historical_consumption=[100, 100, 100],
        growth_multiplier=1.0,
        emergency_shock_factor=0.50,
    )
    assert result["anomaly_detected"] is True
    assert result["surge_percentage"] == "50%"
    assert result["total_projected_demand"] == 1050  # 150 * 7 days


def test_inventory_tool_strategic_reserve_breach():
    """Verify that inventory metrics trigger a breach when below sovereign floor."""
    metrics = calculate_inventory_metrics(
        current_stock=600,
        daily_demand=100.0,
        lead_time_days=3,
        strategic_reserve_floor=500,
    )
    # Post-lead stock = 600 - (100 * 3) = 300 < 500 (breach)
    assert metrics["strategic_reserve_breach"] is True
    assert metrics["reorder_needed"] is True
    assert metrics["recommended_reorder_qty"] > 0


def test_supplier_tool_disruption_delay_integration():
    """Verify that supplier lead times reflect active disruption delays."""
    disruptions = [
        {
            "impacted_supplier_id": "SUP-GLOBAL-02",
            "induced_delay_days": 5,
        }
    ]
    proposals = evaluate_supplier_proposals(quantity_needed=500, disruptions=disruptions)
    global_sup = next(p for p in proposals if p["supplier_id"] == "SUP-GLOBAL-02")
    assert global_sup["disruption_delay_days"] == 5
    assert global_sup["effective_lead_time_days"] == global_sup["base_lead_time_days"] + 5


def test_logistics_tool_critical_dispatch():
    """Verify that critical urgency selects express air freight."""
    dispatch = plan_freight_dispatch(quantity_units=1000, urgency_level="CRITICAL")
    assert dispatch["speed_tier"] == "CRITICAL_EXPRESS"
    assert dispatch["security_certified"] is True
    assert dispatch["transit_days"] == 1


# ==============================================================================
# 2. GUARDRAILS TESTS
# ==============================================================================

def test_embargo_guardrail_veto():
    """Verify that an embargoed origin country receives an immediate veto."""
    passed, msg, audit = validate_embargo_sanctions_guardrail(
        supplier_country="EMBARGO_LAND",
        certified_by_state=False,
    )
    assert passed is False
    assert "STATE SANCTIONS & EMBARGO LIST" in msg
    assert audit["is_sanctioned"] is True


def test_embargo_guardrail_approved():
    """Verify that certified domestic vendor passes sovereignty checks."""
    passed, msg, _ = validate_embargo_sanctions_guardrail(
        supplier_country="DOMESTIC",
        certified_by_state=True,
    )
    assert passed is True
    assert "accredited and compliant" in msg


def test_procurement_budget_guardrail_emergency_waiver():
    """Verify that emergency declaration expands spending ceiling."""
    passed, msg, audit = validate_procurement_budget_guardrail(
        material_cost_eur=180_000.0,
        freight_cost_eur=20_000.0,
        is_emergency_declared=True,
    )
    assert passed is True
    assert audit["effective_ceiling_eur"] == SystemConfig.EMERGENCY_BUDGET_CEILING_EUR


def test_procurement_budget_guardrail_peacetime_violation():
    """Verify that spending over standard ceiling without emergency is rejected."""
    passed, msg, _ = validate_procurement_budget_guardrail(
        material_cost_eur=120_000.0,
        freight_cost_eur=10_000.0,
        is_emergency_declared=False,
    )
    assert passed is False
    assert "exceeds statutory spending ceiling" in msg


def test_strategic_reserve_guardrail_violation():
    """Verify that reserve violation flags correctly."""
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

def test_full_graph_execution():
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
