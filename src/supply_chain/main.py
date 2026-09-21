"""
Interactive CLI Runner for the Sovereign Supply Chain Multi-Agent System.

Demonstrates:
- Official LangGraph StateGraph execution with `.invoke()` and `.stream()`
- Official LangGraph Checkpointer (`MemorySaver`) with thread state inspection (`app.get_state(config)`)
- Official LangGraph conditional edge routing based on sovereign guardrails
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from src.supply_chain.graph import build_supply_chain_graph
from src.supply_chain.config import SystemConfig
from src.supply_chain.reports import export_executive_report

console = Console()



def display_banner():
    """Renders the executive terminal header."""
    header_text = Text()
    header_text.append("🏛️ SOVEREIGN SUPPLY CHAIN MULTI-AGENT SYSTEM\n", style="bold cyan")
    header_text.append("Autonomous Resilient Orchestration with LangGraph & LangChain\n", style="dim white")
    header_text.append("LangGraph Checkpointer (Memory) • @tool Decorators • StateGraph Routing", style="yellow")
    console.print(Panel(header_text, box=box.ROUNDED, expand=False, border_style="cyan"))


def run_crisis_simulation(sku: str = "SKU-MED-901", starting_stock: int = 750):
    """
    Executes an end-to-end crisis simulation through the compiled LangGraph agent graph.

    Args:
        sku (str): Strategic item code.
        starting_stock (int): Starting warehouse physical inventory.
    """
    display_banner()

    console.print(f"\n[bold yellow]⚡ INITIALIZING CRISIS SIMULATION SCENARIO...[/bold yellow]")
    console.print(f"• Item Target: [cyan]{sku}[/cyan] (National Strategic Emergency Supplies)")
    console.print(f"• Starting Warehouse Stock: [white]{starting_stock} units[/white]")
    console.print(f"• Statutory Strategic Reserve Floor: [bold red]{SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR} units[/bold red] (Untouchable)\n")

    # 1. Build workflow with official LangGraph MemorySaver checkpointer
    app = build_supply_chain_graph(checkpointer=True)

    # 2. Setup persistent memory thread config
    thread_id = f"crisis-thread-{datetime.now().strftime('%Y%m%d-%H%M')}"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "sku": sku,
        "sku_description": "Emergency Strategic Medical Supplies & Intensive Care Filters",
        "current_inventory": starting_stock,
        "strategic_reserve_floor": SystemConfig.CRITICAL_STRATEGIC_RESERVE_FLOOR,
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

    console.print(f"[bold green]▶ Running multi-agent graph stream (Thread: {thread_id})...[/bold green]\n")

    agent_style_map = {
        "demand_agent": ("📈 DEMAND FORECASTING AGENT", "blue"),
        "inventory_agent": ("📦 INVENTORY OPTIMIZATION AGENT", "magenta"),
        "risk_agent": ("⚠️ RISK & DISRUPTION RADAR AGENT", "bright_red"),
        "procurement_agent": ("🤝 PROCUREMENT & SOURCING AGENT", "yellow"),
        "compliance_guardrail": ("🛡️ SOVEREIGN GUARDRAIL & COMPLIANCE", "green"),
        "logistics_agent": ("🚚 LOGISTICS & FLEET AGENT", "cyan"),
        "orchestrator_agent": ("👑 MASTER ORCHESTRATOR (CONTROL TOWER)", "bold white on dark_blue"),
    }

    final_state = {}

    # Stream agent nodes step-by-step
    for event in app.stream(initial_state, config=config):
        for node_name, node_output in event.items():
            title, color = agent_style_map.get(node_name, (node_name.upper(), "white"))
            
            # Extract latest BaseMessage from the node
            node_messages = node_output.get("messages", [])
            latest_msg = node_messages[-1].content if node_messages else "Step finished."

            panel = Panel(
                Text(latest_msg, style="white"),
                title=f"[bold {color}]{title}[/bold {color}]",
                border_style=color,
                box=box.ROUNDED,
                padding=(0, 1),
            )
            console.print(panel)
            final_state.update(node_output)

    # 3. Demonstrate Official LangGraph Memory Inspection (app.get_state)
    console.print("\n[bold cyan]🔍 CHECKPOINTER MEMORY STATE INSPECTION (`app.get_state(config)`):[/bold cyan]")
    checkpoint_state = app.get_state(config)
    console.print(f"• Checkpointer Thread ID: [bold white]{config['configurable']['thread_id']}[/bold white]")
    console.print(f"• Persistent Messages in State: [bold green]{len(checkpoint_state.values.get('messages', []))} messages stored[/bold green]")
    console.print(f"• Final Checkpoint Step: [bold yellow]{checkpoint_state.values.get('current_step')}[/bold yellow]")
    console.print(f"• Next Scheduled Node: [bold magenta]{checkpoint_state.next or 'None (Execution Completed)'}[/bold magenta]")

    # 4. Render Executive Final Dashboard
    decision = final_state.get("orchestrator_decision", {})
    if decision:
        console.print("\n")
        table = Table(title="📋 EXECUTIVE SUPPLY CHAIN SUMMARY DECREE", box=box.DOUBLE_EDGE, border_style="gold1")
        table.add_column("Operational Dimension", style="cyan", no_wrap=True)
        table.add_column("Executive Resolution & Details", style="bold white")

        table.add_row("Executive Order ID", decision.get("executive_order_id", "N/A"))
        table.add_row("Verdict Status", f"[bold green]{decision.get('verdict')}[/bold green]")
        table.add_row("Target SKU", f"{decision.get('sku')} - {decision.get('sku_description')}")
        table.add_row("Authorized Vendor", f"{decision.get('authorized_supplier')} ({decision.get('supplier_country')})")
        table.add_row("Replenishment Quantity", f"{decision.get('units_ordered'):,} units")
        table.add_row("Material Cost", f"{decision.get('material_cost_eur', 0):,.2f} EUR")
        table.add_row("Assigned Carrier", f"{decision.get('carrier_assigned')}")
        table.add_row("Logistics Freight Cost", f"{decision.get('freight_cost_eur', 0):,.2f} EUR")
        table.add_row("Total Committed Budget", f"[bold yellow]{decision.get('total_commitment_eur', 0):,.2f} EUR[/bold yellow]")
        table.add_row("Total Cycle Time to Dock", f"[bold cyan]{decision.get('estimated_arrival_days')} days[/bold cyan]")
        table.add_row("Strategic Reserve Buffer", "[green]SECURED & COMPLIANT[/green]")
        table.add_row("Trade-Off Arbitration", decision.get("trade_off_resolution", ""))

        console.print(table)
        console.print(f"\n[bold green]✔ Supply chain crisis successfully resolved under full state compliance.[/bold green]\n")

    # 5. Export Statutory Audit Report to JSON
    report_file = export_executive_report(final_state, thread_id)
    console.print(f"[bold cyan]📁 Statutory Audit Report exported:[/bold cyan] [underline]{report_file}[/underline]\n")


def main():
    """Main CLI entrypoint."""
    run_crisis_simulation()



if __name__ == "__main__":
    main()
