from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA = json.loads(Path("contracts/transfer_card.schema.json").read_text())


def test_transfer_card_validates(client):
    r = client.post("/v1/transfers", json={
        "fromBranch": "branch_a", "toBranch": "branch_b",
        "itemCode": "PARA", "quantity": 1})
    card = r.json()
    jsonschema.validate(card, SCHEMA)
    # camelCase check: no snake_case keys
    for k in card.keys():
        assert "_" not in k


def test_requested_at_format(client):
    r = client.post("/v1/transfers", json={
        "fromBranch": "branch_a", "toBranch": "branch_b",
        "itemCode": "PARA", "quantity": 1})
    ts = r.json()["requestedAt"]
    assert "Z" in ts or "+" in ts


def test_approved_card_validates(client):
    r = client.post("/v1/transfers", json={
        "fromBranch": "branch_a", "toBranch": "branch_b",
        "itemCode": "PARA", "quantity": 1})
    tid = r.json()["id"]
    ar = client.post(f"/v1/transfers/{tid}/approve")
    jsonschema.validate(ar.json(), SCHEMA)


def test_inbox_cards_validate(client):
    client.post("/v1/transfers", json={
        "fromBranch": "branch_a", "toBranch": "branch_b",
        "itemCode": "PARA", "quantity": 1})
    r = client.get("/v1/branches/branch_b/transfers")
    for card in r.json()["items"]:
        jsonschema.validate(card, SCHEMA)
