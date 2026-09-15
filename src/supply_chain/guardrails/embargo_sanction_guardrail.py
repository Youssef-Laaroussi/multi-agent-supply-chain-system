"""
Sovereign Embargo & Sanctions Origin Guardrail.

Enforces state sovereignty regulations, trade sanctions, and supplier security accreditation.
"""

from typing import Dict, Tuple
from src.supply_chain.config import SystemConfig


def validate_embargo_sanctions_guardrail(
    supplier_country: str,
    certified_by_state: bool,
    sanctioned_countries: tuple = SystemConfig.SANCTIONED_COUNTRIES,
) -> Tuple[bool, str, Dict]:
    """
    Validates supplier sovereignty origin against official state sanction lists.

    Args:
        supplier_country (str): Country code or jurisdiction name of the vendor.
        certified_by_state (bool): Whether the supplier holds valid state security certification.
        sanctioned_countries (tuple): Tuple of banned jurisdictions.

    Returns:
        Tuple[bool, str, Dict]:
            - passed (bool): True if vendor is cleared for sovereign government business.
            - message (str): Compliance audit decision.
            - audit (Dict): Inspection details.
    """
    audit = {
        "supplier_country": supplier_country,
        "certified_by_state": certified_by_state,
        "is_sanctioned": supplier_country in sanctioned_countries,
    }

    if supplier_country in sanctioned_countries:
        msg = (
            f"GUARDRAIL_VETO: Supplier origin '{supplier_country}' is on the STATE SANCTIONS & EMBARGO LIST. "
            f"Statutory ban under Sovereign Defense and Trade Regulations."
        )
        return False, msg, audit

    if not certified_by_state:
        msg = (
            f"GUARDRAIL_VETO: Supplier is NOT certified by national authorities. "
            f"Cannot procure strategic goods from unaccredited commercial entities."
        )
        return False, msg, audit

    msg = (
        f"GUARDRAIL_PASSED: Supplier from '{supplier_country}' is accredited and compliant "
        f"with sovereign trade regulations."
    )
    return True, msg, audit
