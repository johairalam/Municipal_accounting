from .models import UserPermission

def user_has_permission(user, code: str) -> bool:
    if not user.is_authenticated:
        return False
    # Root developer has everything
    if getattr(user, 'role', None) == 'ROOT_DEV':
        return True
    return UserPermission.objects.filter(user=user, code=code).exists()

from datetime import date
from decimal import Decimal

from .models import Ledger


def _signed_from_dc(amount, dc):
    """
    Convert amount + 'Dr'/'Cr' to signed number:
    Dr -> positive, Cr -> negative, anything else -> 0.
    """
    amt = float(amount or 0)
    dc = (dc or "").strip().upper()
    if dc == "DR":
        return amt
    if dc == "CR":
        return -amt
    return 0.0


def _compute_opening_suspense_row(current_ulb, tb_rows):
    """
    Compute suspense opening row so that total opening Dr == total opening Cr.

    tb_rows is the list returned by get_trial_balance_rows BEFORE adding suspense.
    Each row has: opening_amount, opening_type ("DR"/"CR"), dr_amount, cr_amount.
    Suspense should be only for opening imbalance.[web:1291]
    """
    total_opening_signed = 0.0
    for row in tb_rows:
        opening_amount = float(row["opening_amount"] or 0)
        opening_type = (row["opening_type"] or "").upper()
        total_opening_signed += _signed_from_dc(
            opening_amount,
            "Dr" if opening_type == "DR" else "Cr" if opening_type == "CR" else "",
        )

    # If already balanced, no suspense row.
    if abs(total_opening_signed) < 0.005:
        return None

    # If total_opening_signed is positive -> more Dr, need Cr suspense to balance.
    # If negative -> more Cr, need Dr suspense to balance.
    if total_opening_signed > 0:
        suspense_opening_amount = abs(total_opening_signed)
        suspense_opening_type = "CR"
    else:
        suspense_opening_amount = abs(total_opening_signed)
        suspense_opening_type = "DR"

    # Create a pseudo-ledger-like row
    class _PseudoLedger:
        def __init__(self, ulb):
            self.id = 0  # not used in db
            self.ulb = ulb
            self.name = "Suspense A/c"

    suspense_ledger = _PseudoLedger(current_ulb)

    return {
        "ledger": suspense_ledger,
        "opening_amount": suspense_opening_amount,
        "opening_type": suspense_opening_type,
        "dr_amount": 0.0,
        "cr_amount": 0.0,
    }

