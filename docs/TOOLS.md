# LangChain `@tool` Specifications & Schemas

This document defines the technical specifications, Pydantic schemas, mathematical formulas, and input/output contracts for all tools in the **Sovereign Supply Chain Multi-Agent System**.

Every tool is built strictly following official LangChain standards using the `@tool(args_schema=...)` decorator.

---

## Table of Contents
1. [Demand Forecasting Tool](#1-demand-forecasting-tool)
2. [Inventory Optimization Tool](#2-inventory-optimization-tool)
3. [Risk & Disruption Radar Tool](#3-risk--disruption-radar-tool)
4. [Supplier Sourcing & Evaluation Tool](#4-supplier-sourcing--evaluation-tool)
5. [Logistics & Fleet Dispatch Tool](#5-logistics--fleet-dispatch-tool)

---

## 1. Demand Forecasting Tool

* **Module:** `src.supply_chain.tools.forecasting_tools`
* **Function:** `calculate_demand_forecast_tool`
* **Agent Binding:** `demand_agent`

### Purpose
Calculates baseline statistical consumption from time-series history, integrates macro growth and crisis shock factors, and detects demand surge anomalies.

### Mathematical Formulation
$$\text{Baseline Daily} = \frac{1}{N} \sum_{i=1}^N \text{Consumption}_i$$
$$\text{Adjusted Daily} = \text{Baseline Daily} \times \text{Growth Multiplier} \times (1 + \text{Shock Factor})$$
$$\text{Total Projected Demand} = \text{Adjusted Daily} \times \text{Planning Horizon (7 days)}$$

### Input Schema (`DemandForecastInput`)
```python
class DemandForecastInput(BaseModel):
    sku: str = Field(description="Unique product SKU, e.g. 'SKU-MED-901'")
    historical_consumption: Optional[List[int]] = Field(default=None, description="Daily units consumed")
    growth_multiplier: float = Field(default=1.0, description="Macro seasonal factor")
    emergency_shock_factor: float = Field(default=0.0, description="Surge multiplier (e.g. 0.80 for +80%)")
```

### Output Keys
| Field | Type | Description |
|---|---|---|
| `baseline_daily_average` | `float` | Raw daily historical mean |
| `adjusted_daily_forecast` | `float` | Shock-adjusted daily rate |
| `planning_horizon_days` | `int` | Standard 7-day planning window |
| `total_projected_demand` | `int` | Total units required over horizon |
| `anomaly_detected` | `bool` | `True` if shock factor exceeds 25% |

---

## 2. Inventory Optimization Tool

* **Module:** `src.supply_chain.tools.inventory_tools`
* **Function:** `calculate_inventory_metrics_tool`
* **Agent Binding:** `inventory_agent`

### Purpose
Computes statistical Reorder Points (ROP), Safety Stock, days of supply remaining, and audits for breaches against the untouchable State Strategic Reserve Floor.

### Mathematical Formulation
$$\text{Safety Stock } (SS) = Z \times \sigma_d \times \sqrt{L}$$
$$\text{Reorder Point } (ROP) = (d \times L) + SS$$
$$\text{Projected Post-Lead Stock} = \text{Current Stock} - (d \times L)$$
$$\text{Strategic Breach} = \text{Projected Post-Lead Stock} < \text{Strategic Reserve Floor}$$

*Where $d$ = daily demand, $L$ = supplier lead time days, $Z$ = normal service factor (1.96 for 95% service level), $\sigma_d$ = standard deviation of demand.*

### Input Schema (`InventoryMetricsInput`)
```python
class InventoryMetricsInput(BaseModel):
    current_stock: int = Field(description="Current on-hand warehouse inventory")
    daily_demand: float = Field(description="Adjusted daily consumption rate")
    lead_time_days: int = Field(default=3, description="Expected delivery lead time")
    demand_std_dev: float = Field(default=20.0, description="Standard deviation of daily demand")
    service_factor_z: float = Field(default=1.96, description="Z-score for 95% service level")
    strategic_reserve_floor: int = Field(default=500, description="Statutory sovereign reserve floor")
```

---

## 3. Risk & Disruption Radar Tool

* **Module:** `src.supply_chain.tools.risk_radar_tools`
* **Function:** `query_risk_radar_tool`
* **Agent Binding:** `risk_agent`

### Purpose
Scans external threat intelligence feeds for maritime disruptions, severe weather, labor strikes, and geopolitical flashpoints, computing induced supplier delays.

### Input Schema (`RiskRadarInput`)
```python
class RiskRadarInput(BaseModel):
    sku: str = Field(description="Product SKU to scan against supply corridors")
    include_weather: bool = Field(default=True, description="Scan meteorological threats")
    include_geopolitical: bool = Field(default=True, description="Scan trade alerts & embargoes")
```

### Threat Classification
* **LOW (0.0 - 0.25):** Normal peacetime transit corridors.
* **MODERATE (0.25 - 0.50):** Localized congestion; minor buffer delays.
* **HIGH (0.50 - 0.75):** Severe storms or union strikes impacting primary lanes.
* **CRITICAL (0.75 - 1.00):** Regional conflict or active embargo activation.

---

## 4. Supplier Sourcing & Evaluation Tool

* **Module:** `src.supply_chain.tools.supplier_tools`
* **Function:** `evaluate_supplier_proposals_tool`
* **Agent Binding:** `procurement_agent`

### Purpose
Queries accredited supplier catalogs, penalizes vendor lead times based on active risk radar delays, and scores proposals by total cost, speed, and reliability.

### Input Schema (`SupplierEvaluationInput`)
```python
class SupplierEvaluationInput(BaseModel):
    quantity_needed: int = Field(description="Total units required for replenishment")
    disruptions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Active disruptions")
```

### Lead-Time Adjustment Logic
$$\text{Effective Lead Time} = \text{Base Lead Time} + \sum \text{Induced Delay Days}$$
$$\text{Total Material Cost} = \text{Quantity Quoted} \times \text{Unit Price (EUR)}$$

---

## 5. Logistics & Fleet Dispatch Tool

* **Module:** `src.supply_chain.tools.logistics_tools`
* **Function:** `plan_freight_dispatch_tool`
* **Agent Binding:** `logistics_agent`

### Purpose
Allocates security-certified transportation fleets (State Air Express, Trans-Continental Road, Intermodal Rail) based on urgency tier, computing transit times and freight costs.

### Input Schema (`LogisticsDispatchInput`)
```python
class LogisticsDispatchInput(BaseModel):
    quantity_units: int = Field(description="Quantity of units to transport")
    urgency_level: str = Field(default="STANDARD", description="'STANDARD' or 'CRITICAL'")
    require_security_escort: bool = Field(default=False, description="State military/security escort flag")
```

### Fleet Routing Matrix
| Speed Tier | Carrier Entity | Transit Days | Cost / Unit | Certified Security |
|---|---|:---:|:---:|:---:|
| `CRITICAL_EXPRESS` | National Sovereign Air Express | 1 day | 15.00 € | Yes |
| `STANDARD_ROAD` | Trans-Continental Freight Fleet | 3 days | 5.00 € | Yes |
| `ECONOMY_SLOW` | SlowRail Maritime & Intermodal | 7 days | 1.50 € | No |
