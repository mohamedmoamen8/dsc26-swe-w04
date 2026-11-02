"""Unit tests for nour_transfers.rules."""

from __future__ import annotations

import math

import pytest

from nour_transfers import rules


# --- days_of_cover ---------------------------------------------------------

def test_days_of_cover_basic():
    assert rules.days_of_cover(100, 5.0) == 20.0


def test_days_of_cover_zero_sales_returns_none():
    assert rules.days_of_cover(100, 0) is None


def test_days_of_cover_negative_stock_raises():
    with pytest.raises(ValueError):
        rules.days_of_cover(-1, 1.0)


def test_days_of_cover_negative_sales_raises():
    with pytest.raises(ValueError):
        rules.days_of_cover(10, -0.5)


def test_days_of_cover_fractional_sales():
    assert rules.days_of_cover(10, 3.0) == pytest.approx(10 / 3)


# --- priority --------------------------------------------------------------

def test_priority_none_is_normal():
    assert rules.priority(False, None) == "normal"
    assert rules.priority(True, None) == "normal"


def test_priority_urgent_chronic_low_cover():
    assert rules.priority(True, 2.9) == "urgent"


def test_priority_urgent_boundary_exactly_3_is_not_urgent():
    # cover of exactly 3 days must NOT be urgent (strictly less than 3)
    assert rules.priority(True, 3.0) == "high"


def test_priority_high_under_7():
    assert rules.priority(False, 5.0) == "high"
    assert rules.priority(True, 6.9) == "high"


def test_priority_high_boundary_exactly_7_is_normal():
    assert rules.priority(False, 7.0) == "normal"


def test_priority_normal_high_cover():
    assert rules.priority(True, 10.0) == "normal"
    assert rules.priority(False, 100.0) == "normal"


def test_priority_non_chronic_low_cover_not_urgent():
    # Non-chronic items with low cover must NOT become urgent
    assert rules.priority(False, 1.0) == "high"


# --- can_transfer ----------------------------------------------------------

def test_can_transfer_quantity_one_ok():
    assert rules.can_transfer(100, 1, 20) is True


def test_can_transfer_zero_quantity_fails():
    # M02: zero quantity must be rejected
    assert rules.can_transfer(100, 0, 20) is False


def test_can_transfer_negative_quantity_fails():
    assert rules.can_transfer(100, -5, 20) is False


def test_can_transfer_below_reserve_fails():
    # stock 50, quantity 40, reserve 20 -> 50-40=10 < 20
    assert rules.can_transfer(50, 40, 20) is False


def test_can_transfer_at_reserve_boundary_ok():
    # stock 50, quantity 30, reserve 20 -> 50-30=20 == reserve, allowed
    assert rules.can_transfer(50, 30, 20) is True


def test_can_transfer_off_by_one_reserve_fails():
    # stock 50, quantity 31, reserve 20 -> 50-31=19 < 20
    assert rules.can_transfer(50, 31, 20) is False


def test_can_transfer_zero_reserve_ok():
    assert rules.can_transfer(10, 10, 0) is True


def test_can_transfer_insufficient_stock():
    assert rules.can_transfer(5, 10, 0) is False