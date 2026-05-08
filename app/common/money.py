# BAG — Budgeting Aid Guide
# Copyright © 2026 Group_0
# All Rights Reserved
def money_to_cents(value: str) -> int | None:
    try:
        amount = float(value)
    except Exception:
        return None
    if amount < 0:
        return None
    return int(round(amount * 100))


def cents_to_money(cents: int) -> float:
    return (cents or 0) / 100.0

