# Sovereign Guardrails Specifications

This document defines the formal guardrails governing the Multi-Agent Supply Chain System.

---

## 1. Statutory Strategic Reserve Floor Guardrail

* **Module:** `src.supply_chain.guardrails.strategic_reserve_guardrail`
* **Function:** `validate_strategic_reserve_guardrail`
* **Legal Policy:** The State decrees a permanent, untouchable strategic reserve baseline of critical goods (medical equipment, grid components, survival rations) to guarantee civil protection during crises.

### Formula:
$$\text{Net Projected Stock} = \text{Current Stock} - \text{Lead Time Outflow} + \text{Confirmed Replenishment}$$

### Enforcement Rule:
$$\text{Net Projected Stock} \ge \text{CRITICAL\_STRATEGIC\_RESERVE\_FLOOR} \quad (\text{Default: } 500 \text{ units})$$

* **Outcome if Violated:** `GUARDRAIL_VIOLATION`. Triggers urgent reorder and activates the public emergency procurement procedure.

---

## 2. Public Procurement Budget & Fiscal Ceiling Guardrail

* **Module:** `src.supply_chain.guardrails.procurement_budget_guardrail`
* **Function:** `validate_procurement_budget_guardrail`
* **Legal Policy:** Enforces public finance oversight, anti-corruption controls, and spending limits under public procurement statutes.

### Thresholds:
| Parameter | Value (EUR) | Purpose |
| :--- | :--- | :--- |
| `MAX_EXPRESS_PURCHASE_BUDGET_EUR` | 100,000.00 € | Peacetime standard discretionary spending cap. |
| `EMERGENCY_BUDGET_CEILING_EUR` | 250,000.00 € | Fast-track emergency spending ceiling under declared crisis. |
| `SOLE_SOURCE_JUSTIFICATION_THRESHOLD_EUR` | 25,000.00 € | Threshold requiring formal sole-source justification memo. |

### Enforcement Logic:
1. If $\text{Total Expenditure} > \text{Effective Ceiling}$: **STRICT REJECTION**.
2. If $\text{Total Expenditure} > \text{Sole Source Threshold}$ without active emergency: Emits a compliance warning requiring fast-track countersignature.

---

## 3. Sovereign Embargo & Sanctions Guardrail

* **Module:** `src.supply_chain.guardrails.embargo_sanction_guardrail`
* **Function:** `validate_embargo_sanctions_guardrail`
* **Legal Policy:** Sovereign supply chains must never depend on hostile foreign adversaries or uncertified suppliers for strategic survival goods.

### Rules:
1. **Sanctions Check:** If vendor country is in `SANCTIONED_COUNTRIES` (`EMBARGO_LAND`, `UNAPPROVED_OFFSHORE`, `NON_CERTIFIED_TERRITORY`), an immediate **VETO** is issued.
2. **State Certification Check:** Supplier must have `certified_by_state == True`.
3. **Automated Remediating Search:** When a commercial vendor is vetoed, the Guardrail automatically searches the proposals list for the highest-ranking certified domestic alternative.
