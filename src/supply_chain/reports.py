"""
Audit and Reporting module for the Sovereign Supply Chain MAS.

Exports complete crisis execution states and executive decrees to structured JSON
reports for statutory compliance and enterprise auditing.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict


def export_executive_report(
    final_state: Dict[str, Any],
    thread_id: str,
    output_dir: str = "reports",
) -> str:
    """
    Exports the complete multi-agent crisis resolution audit trail to a formatted JSON report.

    Args:
        final_state: The final state dictionary returned by the LangGraph execution.
        thread_id: The unique execution thread identifier.
        output_dir: Directory where the report file will be saved.

    Returns:
        str: Absolute filepath of the generated report.
    """
    os.makedirs(output_dir, exist_ok=True)

    sku = final_state.get("sku", "UNKNOWN_SKU")
    timestamp_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"decree_{sku}_{timestamp_slug}.json"
    filepath = os.path.join(output_dir, filename)

    # Extract messages safely (convert BaseMessage to serializable dicts)
    serialized_messages = []
    for msg in final_state.get("messages", []):
        if hasattr(msg, "content"):
            serialized_messages.append({
                "type": getattr(msg, "type", "message"),
                "name": getattr(msg, "name", "agent"),
                "content": msg.content,
            })
        elif isinstance(msg, dict):
            serialized_messages.append(msg)

    report_payload = {
        "metadata": {
            "title": "Sovereign Supply Chain MAS - Statutory Crisis Resolution Decree",
            "report_id": f"REP-{timestamp_slug}",
            "generated_at": datetime.now().isoformat(),
            "thread_id": thread_id,
            "system_version": "1.0.0",
        },
        "target_context": {
            "sku": sku,
            "sku_description": final_state.get("sku_description", ""),
            "starting_warehouse_stock": final_state.get("current_inventory"),
            "statutory_reserve_floor": final_state.get("strategic_reserve_floor"),
        },
        "executive_decision": final_state.get("orchestrator_decision", {}),
        "compliance_audit": final_state.get("compliance_review", {}),
        "pipeline_stages": {
            "demand_forecast": final_state.get("demand_forecast", {}),
            "inventory_analysis": final_state.get("inventory_analysis", {}),
            "risk_assessment": final_state.get("risk_assessment", {}),
            "logistics_plan": final_state.get("logistics_plan", {}),
        },
        "agent_logs": final_state.get("agent_logs", []),
        "agent_messages": serialized_messages,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2, ensure_ascii=False)

    return filepath
