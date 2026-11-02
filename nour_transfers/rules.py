"""Business rules for the Nour transfers service."""

from __future__ import annotations

from typing import Optional


def days_of_cover(stock: int, avg_daily_sales: float) -> Optional[float]:
    """Return stock divided by average daily sales.

    Returns None when avg_daily_sales is zero (lasts indefinitely).
    Raises ValueError for negative inputs.
    """
    if stock < 0 or avg_daily_sales < 0:
        raise ValueError("stock and avg_daily_sales must be non-negative")
    if avg_daily_sales == 0:
        return None
    return stock / avg_daily_sales


def priority(is_chronic: bool, cover_days: Optional[float]) -> str:
    """Return priority for an item.

    - normal if cover_days is None
    - urgent if is_chronic and cover_days is not None and cover_days < 3
    - high if cover_days is not None and cover_days < 7
    - normal otherwise
    """
    if cover_days is None:
        return "normal"
    if is_chronic and cover_days < 3:
        return "urgent"
    if cover_days < 7:
        return "high"
    return "normal"


def can_transfer(from_stock: int, quantity: int, reserve: int) -> bool:
    """Return True if a transfer is allowed.

    Quantity must be at least 1, and the sending branch must keep
    at least the item's reserve afterwards.
    """
    if quantity < 1:
        return False
    if from_stock - quantity < reserve:
        return False
    return True