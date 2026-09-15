# Architecture Specifications: LangGraph Multi-Agent Supply Chain System

## 1. Graph State Model

The state of the system is governed by `SupplyChainState`, a typed dictionary inheriting from `typing_extensions.TypedDict` and incorporating official LangGraph message reducers:

```python
class SupplyChainState(TypedDict):
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

    messages: Annotated[List[BaseMessage], add_messages]
    agent_logs: Annotated[List[str], operator.add]

    current_step: str
    is_compliant: bool
    is_completed: bool
```

### Key Properties:
* **`messages`**: Uses `Annotated[List[BaseMessage], add_messages]`. Every agent produces an `AIMessage(content=..., name=...)` that is automatically merged into the conversation history by LangGraph.
* **`agent_logs`**: Uses `operator.add` to maintain an immutable append-only audit trail of every operational action.
* **`is_compliant`**: Acts as the gatekeeper for the conditional edge routing.

---

## 2. Execution Flow & State Transitions

1. **START -> `demand_agent`**:
   - Calculates baseline consumption.
   - Detects crisis anomalies and emergency surge multipliers.
   - Emits 7-day projected demand.

2. **`demand_agent` -> `inventory_agent`**:
   - Calculates dynamic Safety Stock and Reorder Point (ROP).
   - Audits projected stock against the statutory 500-unit State Strategic Reserve Floor.
   - Triggers critical breach warning and computes required replenishment quantity.

3. **`inventory_agent` -> `risk_agent`**:
   - Scans environmental threat vectors (weather hubs, maritime choke points).
   - Flags active embargo and sanction alerts.
   - Assigns threat scores and supplier-specific delays.

4. **`risk_agent` -> `procurement_agent`**:
   - Queries vendor catalog for quotes.
   - Applies risk-induced lead-time penalties.
   - Selects preliminary sourcing candidate.

5. **`procurement_agent` -> `compliance_guardrail`**:
   - Executes the 3 Sovereign Guardrails:
     1. Embargo and origin verification.
     2. Public budget ceiling validation.
     3. Strategic reserve floor protection.
   - Possesses statutory veto power. If a tentative vendor fails, scans for compliant certified domestic alternatives.

6. **Conditional Edge (`guardrail_conditional_router`)**:
   - **Branch A (Compliant)**: Routes to `logistics_agent` for carrier allocation.
   - **Branch B (Non-Compliant)**: Bypasses logistics and routes directly to `orchestrator_agent` for emergency halt decree.

7. **`logistics_agent` -> `orchestrator_agent`**:
   - Selects security-certified fleet (Air Express, Road Fleet).
   - Determines freight cost and transit schedule.

8. **`orchestrator_agent` -> END**:
   - Issues binding Executive Order (`EX-DECREE-...`).
   - Balances operational trade-offs and finalizes budget allocation.

---

## 3. Memory & Checkpointing

The compiled graph uses `MemorySaver` from `langgraph.checkpoint.memory`:
```python
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
```
Each run is identified by a unique `configurable={"thread_id": "..."}`. Checkpoints record:
- The exact state at every node boundary.
- Full message replay capability.
- Human-in-the-loop inspection and pause/resume capability.
