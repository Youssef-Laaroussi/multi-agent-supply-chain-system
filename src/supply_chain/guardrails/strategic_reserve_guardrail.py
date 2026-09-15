"""
Sovereign Strategic Reserve Guardrail.

Guarantees that warehouse stock levels do not breach the non-negotiable
State Strategic Reserve Floor under peacetime or crisis operations.
"""

from typing import Dict, Tuple
from src.supply_chain.config import SystemConfig


def validate_strategic_reserve_guardrail(
    current_stock: int,
    projected_outflow: int,
    replenishment_incoming: int = 0,
    reserve_floor: int = SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR,
) -> Tuple[bool, str, Dict]:
    """
    Validates if inventory operations preserve the mandatory national reserve floor.

    Args:
        current_stock (int): Starting warehouse physical stock.
        projected_outflow (int): Expected units drained by demand over lead time.
        replenishment_incoming (int): Confirmed replenishment arriving before stockout.
        reserve_floor (int): Minimum strategic reserve floor (default 500).

    Returns:
        Tuple[bool, str, Dict]:
            - passed (bool): True if reserve floor is preserved.
            - message (str): Human-readable audit message.
            - metrics (Dict): Detailed calculation snapshot.
    """
    net_projected_stock = current_stock - projected_outflow + replenishment_incoming

    metrics = {
        "current_stock": current_stock,
        "projected_outflow": projected_outflow,
        "replenishment_incoming": replenishment_incoming,
        "net_projected_stock": net_projected_stock,
        "strategic_reserve_floor": reserve_floor,
        "buffer_margin": net_projected_stock - reserve_floor,
    }

    if net_projected_stock < reserve_floor:
        msg = (
            f"GUARDRAIL_VIOLATION: Net projected stock ({net_projected_stock} units) "
            f"breaches statutory reserve floor ({reserve_floor} units) by "
            f"{abs(net_projected_stock - reserve_floor)} units. Mandatory replenishment required!"
        )
        return False, msg, metrics

    msg = (
        f"GUARDRAIL_PASSED: Net projected stock ({net_projected_stock} units) preserves "
        f"sovereign floor ({reserve_floor} units) with safety margin of {metrics['buffer_margin']} units."
    )
    return True, msg, metrics
