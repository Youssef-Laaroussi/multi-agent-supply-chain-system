"""
Structured Pydantic Schemas for Agent Outputs and State Verification.

Enforces strong typing across all 7 specialized nodes in the Sovereign MAS.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DemandForecastOutput(BaseModel):
    """Output schema for DemandForecastingAgent."""
    sku: str = Field(description="Strategic SKU identifier")
    baseline_daily_average: float = Field(description="Historical baseline daily demand")
    adjusted_daily_forecast: float = Field(description="Daily forecast adjusted for growth and shock")
    planning_horizon_days: int = Field(default=7, description="Planning window in days")
    total_projected_demand: int = Field(description="Total projected units over planning horizon")
    emergency_shock_factor: float = Field(default=0.0, description="Applied shock factor")
    surge_percentage: str = Field(description="Surge percentage representation")
    anomaly_detected: bool = Field(description="Whether a crisis consumption anomaly is detected")


class InventoryMetricsOutput(BaseModel):
    """Output schema for InventoryOptimizationAgent."""
    current_stock: int = Field(description="Current warehouse physical inventory")
    daily_demand: float = Field(description="Adjusted daily consumption rate")
    lead_time_days: int = Field(description="Replenishment lead time in days")
    days_of_supply: float = Field(description="Days of inventory remaining")
    safety_stock: int = Field(description="Calculated buffer safety stock")
    reorder_point: int = Field(description="Statistical Reorder Point (ROP)")
    projected_post_lead_stock: int = Field(description="Projected stock after lead time without reorder")
    reorder_needed: bool = Field(description="Flag indicating replenishment is required")
    recommended_reorder_qty: int = Field(description="Recommended reorder batch quantity")
    strategic_reserve_floor: int = Field(description="Statutory minimum strategic reserve floor")
    strategic_reserve_breach: bool = Field(description="Whether strategic floor will be breached")


class DisruptionAlert(BaseModel):
    """Single disruption event from external risk intelligence."""
    id: str = Field(description="Alert identifier")
    type: str = Field(description="Disruption category (e.g. WEATHER, PORT_STRIKE, GEOPOLITICAL)")
    severity: str = Field(description="Severity rating (LOW, MEDIUM, HIGH, CRITICAL)")
    impacted_supplier_id: str = Field(description="Supplier ID impacted by the event")
    induced_delay_days: int = Field(description="Additional delivery delay in days")
    description: str = Field(description="Human-readable event summary")


class RiskAssessmentOutput(BaseModel):
    """Output schema for RiskRadarAgent."""
    sku: str = Field(description="Evaluated product SKU")
    overall_risk_index: float = Field(description="Aggregate threat score from 0.0 to 1.0")
    risk_level: str = Field(description="Risk categorization (LOW, MODERATE, HIGH, CRITICAL)")
    disruptions: List[DisruptionAlert] = Field(default_factory=list, description="Active disruptions")
    active_alerts_count: int = Field(description="Total number of active threat alerts")


class SupplierProposalOutput(BaseModel):
    """Individual vendor bid evaluated by ProcurementAgent."""
    supplier_id: str = Field(description="Unique supplier ID")
    supplier_name: str = Field(description="Supplier commercial entity name")
    country: str = Field(description="Supplier country of origin")
    certified_by_state: bool = Field(description="Whether certified by sovereign state authorities")
    base_lead_time_days: int = Field(description="Nominal lead time in days")
    disruption_delay_days: int = Field(default=0, description="Delay penalty from risk radar")
    effective_lead_time_days: int = Field(description="Base lead time plus disruption delay")
    unit_price_eur: float = Field(description="Unit purchase price in EUR")
    quantity_quoted: int = Field(description="Units included in the quotation")
    total_material_cost_eur: float = Field(description="Total purchase expenditure")
    reliability_score: float = Field(description="Historical supplier delivery score (0.0 to 1.0)")


class ComplianceReviewOutput(BaseModel):
    """Output schema for SovereignGuardrailValidator."""
    status: str = Field(description="'APPROVED' or 'REJECTED_VETO'")
    reason: str = Field(description="Official audit explanation of the compliance verdict")
    reserve_floor_check: Dict[str, Any] = Field(default_factory=dict, description="Strategic floor audit")
    budget_check: Dict[str, Any] = Field(default_factory=dict, description="Public spending cap audit")
    sanctions_check: Dict[str, Any] = Field(default_factory=dict, description="Embargo and origin audit")
    timestamp: str = Field(description="ISO timestamp of the compliance evaluation")


class LogisticsPlanOutput(BaseModel):
    """Output schema for LogisticsFleetAgent."""
    carrier_id: str = Field(description="Assigned transport carrier identifier")
    carrier_name: str = Field(description="Commercial name of the carrier fleet")
    speed_tier: str = Field(description="Speed category (CRITICAL_EXPRESS, STANDARD_ROAD, ECONOMY_SLOW)")
    transit_days: int = Field(description="Days required for transport delivery")
    rate_per_unit_eur: float = Field(description="Freight shipping cost per unit in EUR")
    quantity_shipped: int = Field(description="Units transported")
    total_freight_cost_eur: float = Field(description="Total freight expenditure in EUR")
    security_certified: bool = Field(description="Whether carrier possesses state security accreditation")
    dispatch_order_id: str = Field(description="Tracking identifier for the freight dispatch")


class OrchestratorDecisionOutput(BaseModel):
    """Output schema for MasterOrchestratorAgent (Executive Decree)."""
    executive_order_id: str = Field(description="Unique statutory decree identifier")
    sku: str = Field(description="Strategic item code")
    sku_description: str = Field(description="Item description")
    verdict: str = Field(description="'AUTHORIZED_AND_DISPATCHED' or 'HALTED_BY_GOVERNANCE'")
    authorized_supplier: str = Field(description="Selected vendor entity")
    supplier_country: str = Field(description="Jurisdiction of the vendor")
    units_ordered: int = Field(description="Final order quantity")
    material_cost_eur: float = Field(description="Total supplier procurement cost")
    carrier_assigned: str = Field(description="Selected transport carrier")
    freight_cost_eur: float = Field(description="Total freight transit cost")
    total_commitment_eur: float = Field(description="Total public expenditure committed")
    estimated_arrival_days: int = Field(description="End-to-end delivery cycle time")
    strategic_reserve_secured: bool = Field(description="Whether strategic buffer is legally secured")
    trade_off_resolution: str = Field(description="Executive rationale for trade-off decisions")
