"""
Public Procurement Budget & Financial Compliance Guardrail.

Enforces public spending limits, threshold escalations, and fiscal accountability rules.
"""

from typing import Dict, Tuple
from src.supply_chain.config import SystemConfig


def validate_procurement_budget_guardrail(
    material_cost_eur: float,
    freight_cost_eur: float,
    budget_ceiling_eur: float = SystemConfig.MAX_EXPRESS_PURCHASE_BUDGET_EUR,
    sole_source_threshold_eur: float = SystemConfig.SOLE_SOURCE_JUSTIFICATION_THRESHOLD_EUR,
    is_emergency_declared: bool = False,
) -> Tuple[bool, str, Dict]:
    """
    Validates expenditure against public procurement budget ceilings and oversight thresholds.

    Args:
        material_cost_eur (float): Total goods purchasing cost.
        freight_cost_eur (float): Total transportation & logistics cost.
        budget_ceiling_eur (float): Maximum allowed commitment per single order.
        sole_source_threshold_eur (float): Level requiring formal competitive justification.
        is_emergency_declared (bool): Whether fast-track public emergency procedure is active.

    Returns:
        Tuple[bool, str, Dict]:
            - passed (bool): True if expenditure meets legal procurement standards.
            - message (str): Compliance determination message.
            - audit (Dict): Detailed breakdown of budget allocation.
    """
    effective_ceiling = (
        SystemConfig.EMERGENCY_BUDGET_CEILING_EUR
        if is_emergency_declared
        else budget_ceiling_eur
    )
    total_expenditure = material_cost_eur + freight_cost_eur

    audit = {
        "material_cost_eur": material_cost_eur,
        "freight_cost_eur": freight_cost_eur,
        "total_expenditure_eur": total_expenditure,
        "effective_ceiling_eur": effective_ceiling,
        "base_budget_ceiling_eur": budget_ceiling_eur,
        "sole_source_threshold_eur": sole_source_threshold_eur,
        "is_emergency_declared": is_emergency_declared,
    }

    if total_expenditure > effective_ceiling:
        msg = (
            f"GUARDRAIL_VIOLATION: Total expenditure ({total_expenditure:,.2f} EUR) exceeds "
            f"statutory spending ceiling ({effective_ceiling:,.2f} EUR). Order cannot be authorized."
        )
        return False, msg, audit

    if total_expenditure > sole_source_threshold_eur and not is_emergency_declared:
        msg = (
            f"GUARDRAIL_WARNING: Order value ({total_expenditure:,.2f} EUR) exceeds sole-source "
            f"threshold ({sole_source_threshold_eur:,.2f} EUR). Requires fast-track emergency decree."
        )
        return True, msg, audit

    msg = (
        f"GUARDRAIL_PASSED: Expenditure ({total_expenditure:,.2f} EUR) is within authorized "
        f"public procurement limits (Ceiling: {budget_ceiling_eur:,.2f} EUR)."
    )
    return True, msg, audit
