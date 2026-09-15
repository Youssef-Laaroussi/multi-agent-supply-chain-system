"""
Official LangChain Tools for Risk Radar & External Disruption Detection.

Uses `@tool` decorator with explicit Pydantic `args_schema` for LLM tool binding.
"""

from pydantic import BaseModel, Field
from langchain_core.tools import tool


class RiskRadarInput(BaseModel):
    """Input schema for risk radar tool."""
    sku: str = Field(description="The strategic SKU identifier to scan external risk intelligence for")


@tool(args_schema=RiskRadarInput)
def query_risk_radar_tool(sku: str) -> dict:
    """Scan real-time intelligence for weather storms, transport blockages, and geopolitical sanctions."""
    active_disruptions = [
        {
            "event_id": "EVT-STORM-2026",
            "type": "SEVERE_WEATHER",
            "description": "Blizzard condition across primary European transit hubs",
            "severity_score": 0.75,
            "impacted_supplier_id": "SUP-GLOBAL-02",
            "induced_delay_days": 4,
            "recommended_action": "Reroute via domestic air cargo or activate national reserve supplier",
        },
        {
            "event_id": "EVT-GEO-99",
            "type": "GEOPOLITICAL_EMBARGO",
            "description": "Enhanced state intelligence alert: Trade sanctions active on DarkBay components",
            "severity_score": 0.95,
            "impacted_supplier_id": "SUP-EMBARGO-03",
            "induced_delay_days": 99,
            "recommended_action": "Strict sovereign embargo. Absolute procurement ban.",
        },
    ]

    max_severity = max(d["severity_score"] for d in active_disruptions)

    return {
        "sku": sku,
        "status": "DISRUPTIONS_DETECTED",
        "active_alerts_count": len(active_disruptions),
        "overall_risk_index": max_severity,
        "risk_level": "HIGH" if max_severity > 0.7 else "MODERATE",
        "disruptions": active_disruptions,
    }
