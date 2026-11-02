"""Shared fixtures for the Nour transfers test suite."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

import pytest
from fastapi.testclient import TestClient

from nour_transfers.app import create_app


def fixed_now():
    return datetime(2026, 10, 29, 12, 0, 0, tzinfo=timezone.utc)


def base_stock() -> Dict[str, Dict[str, int]]:
    return {
        "branch_a": {"PARA": 100, "AMOX": 50},
        "branch_b": {"PARA": 20, "AMOX": 10},
    }


def base_items() -> Dict[str, Dict]:
    return {
        "PARA": {"chronic": False, "reserve": 20},
        "AMOX": {"chronic": True, "reserve": 10},
    }


def base_sales() -> Dict[str, Dict[str, float]]:
    return {
        "branch_a": {"PARA": 5.0, "AMOX": 2.0},
        "branch_b": {"PARA": 0.0, "AMOX": 1.0},
    }


@pytest.fixture
def client():
    app = create_app(base_stock(), base_items(), base_sales(), fixed_now)
    return TestClient(app)


@pytest.fixture
def make_client():
    def _make(stock=None, items=None, sales=None, now=None):
        return TestClient(
            create_app(
                stock if stock is not None else base_stock(),
                items if items is not None else base_items(),
                sales if sales is not None else base_sales(),
                now if now is not None else fixed_now,
            )
        )
    return _make