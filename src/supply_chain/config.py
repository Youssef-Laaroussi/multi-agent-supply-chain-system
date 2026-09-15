"""
Configuration module for the Sovereign Multi-Agent Supply Chain System.

This module defines central operational parameters, public procurement guardrails,
state strategic reserve floors, and mock enterprise databases (suppliers, logistics, sanctions).
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class SystemConfig:
    """Core parameters and sovereign compliance boundaries."""

    # Sovereign Reserve Minimums (Units that must never be breached)
    CRITICAL_STRATEGIC_RESERVE_FLOOR: int = 500

    # Public Procurement Spending Caps (in EUR)
    MAX_EXPRESS_PURCHASE_BUDGET_EUR: float = 100_000.0
    SOLE_SOURCE_JUSTIFICATION_THRESHOLD_EUR: float = 25_000.0

    # Sanctioned Countries / Non-Certified Jurisdictions (Sovereignty Rule)
    SANCTIONED_COUNTRIES: tuple = ("EMBARGO_LAND", "UNAPPROVED_OFFSHORE", "NON_CERTIFIED_TERRITORY")

    # Critical Items Monitored by the State
    STRATEGIC_SKUS: tuple = (
        "SKU-MED-901",  # Emergency Medical Critical Ventilators / Masks
        "SKU-ENG-404",  # Grid Infrastructure Emergency Power Cells
        "SKU-FOOD-101", # National Strategic Food Ration Packs
    )


# Catalog of available suppliers with sovereign accreditation and reliability scores
SUPPLIER_CATALOG: List[Dict] = [
    {
        "id": "SUP-DOMESTIC-01",
        "name": "Hexagon National Strategic Industries",
        "country": "DOMESTIC",
        "certified_by_state": True,
        "lead_time_days": 2,
        "unit_price_eur": 120.0,
        "capacity_units": 1500,
        "reliability_score": 0.98,
        "description": "Domestic certified partner with sovereign fast-track clearance.",
    },
    {
        "id": "SUP-GLOBAL-02",
        "name": "Pan-Euro Logistics & Supplies",
        "country": "ALLIED_EU",
        "certified_by_state": True,
        "lead_time_days": 5,
        "unit_price_eur": 95.0,
        "capacity_units": 3000,
        "reliability_score": 0.91,
        "description": "Reliable allied supplier, optimal cost for scheduled reorders.",
    },
    {
        "id": "SUP-EMBARGO-03",
        "name": "DarkBay Grey-Market Components",
        "country": "EMBARGO_LAND",
        "certified_by_state": False,
        "lead_time_days": 1,
        "unit_price_eur": 60.0,
        "capacity_units": 5000,
        "reliability_score": 0.65,
        "description": "Cheap and fast, but under international embargo and uncertified.",
    },
]

# Carrier options for logistics orchestration
CARRIER_CATALOG: List[Dict] = [
    {
        "id": "CARRIER-STATE-AIR",
        "name": "National Sovereign Air Express",
        "speed_tier": "CRITICAL_EXPRESS",
        "transit_days": 1,
        "cost_per_unit_eur": 15.0,
        "certified_security": True,
    },
    {
        "id": "CARRIER-EURO-ROAD",
        "name": "Trans-Continental Freight Fleet",
        "speed_tier": "STANDARD_ROAD",
        "transit_days": 3,
        "cost_per_unit_eur": 5.0,
        "certified_security": True,
    },
    {
        "id": "CARRIER-LOW-ECO",
        "name": "SlowRail Maritime & Intermodal",
        "speed_tier": "ECONOMY_SLOW",
        "transit_days": 7,
        "cost_per_unit_eur": 1.5,
        "certified_security": False,
    },
]
