"""Synthetic checkout rules for a bounded compatibility experiment."""


def delivery_pence(subtotal_pence, member=False):
    if subtotal_pence < 0:
        raise ValueError("subtotal must not be negative")
    if member or subtotal_pence >= 5000:
        return 0
    return 399


def can_refund(role, shipped):
    return role == "manager" or (role == "agent" and not shipped)
