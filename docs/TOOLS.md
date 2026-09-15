# Official LangChain @tool Suite Reference

All deterministic operations in the Multi-Agent Supply Chain System are implemented as official LangChain `BaseTool` instances using the `@tool(args_schema=...)` decorator from `langchain_core.tools`.

---

## 1. `calculate_demand_forecast_tool`

* **Source:** `src.supply_chain.tools.forecasting_tools`
* **Decorator:** `@tool(args_schema=DemandForecastInput)`

### Input Schema (`DemandForecastInput`):
```python
class DemandForecastInput(BaseModel):
    sku: str
    historical_consumption: Optional[List[int]] = None
    growth_multiplier: float = 1.0
    emergency_shock_factor: float = 0.0
```

### Returns:
```json
{
  "sku": "SKU-MED-901",
  "baseline_daily_average": 125.0,
  "adjusted_daily_forecast": 247.5,
  "planning_horizon_days": 7,
  "total_projected_demand": 1732,
  "emergency_shock_factor": 0.8,
  "surge_percentage": "80%",
  "anomaly_detected": true
}
```

---

## 2. `calculate_inventory_metrics_tool`

* **Source:** `src.supply_chain.tools.inventory_tools`
* **Decorator:** `@tool(args_schema=InventoryMetricsInput)`

### Input Schema (`InventoryMetricsInput`):
```python
class InventoryMetricsInput(BaseModel):
    current_stock: int
    daily_demand: float
    lead_time_days: int = 3
    demand_std_dev: float = 15.0
    service_factor_z: float = 1.96
    strategic_reserve_floor: int = 500
```

### Key Calculations:
* **Safety Stock ($SS$):** $Z \times \sigma_d \times \sqrt{L}$
* **Reorder Point ($ROP$):** $(d \times L) + SS$
* **Strategic Breach Flag:** $\text{Current Stock} - (d \times L) < \text{Strategic Floor}$

---

## 3. `query_risk_radar_tool`

* **Source:** `src.supply_chain.tools.risk_radar_tools`
* **Decorator:** `@tool(args_schema=RiskRadarInput)`

### Input Schema (`RiskRadarInput`):
```python
class RiskRadarInput(BaseModel):
    sku: str
```

### Returns:
Disruption objects containing `severity_score`, `impacted_supplier_id`, and `induced_delay_days`.

---

## 4. `evaluate_supplier_proposals_tool`

* **Source:** `src.supply_chain.tools.supplier_tools`
* **Decorator:** `@tool(args_schema=SupplierEvaluationInput)`

### Input Schema (`SupplierEvaluationInput`):
```python
class SupplierEvaluationInput(BaseModel):
    quantity_needed: int
    disruptions: Optional[List[Dict[str, Any]]] = None
```

### Output:
Ranked list of quotes with base lead time, risk delays, total material costs, and security certifications.

---

## 5. `plan_freight_dispatch_tool`

* **Source:** `src.supply_chain.tools.logistics_tools`
* **Decorator:** `@tool(args_schema=FreightDispatchInput)`

### Input Schema (`FreightDispatchInput`):
```python
class FreightDispatchInput(BaseModel):
    quantity_units: int
    urgency_level: str = "HIGH"
    require_security_escort: bool = True
```

### Output:
Allocated fleet (e.g. `National Sovereign Air Express`), speed tier, transit ETA, security clearance, and total freight expenditure.
