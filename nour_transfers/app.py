"""Nour transfers FastAPI application."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from nour_transfers import rules

ALLOWED_ORIGINS = [
    "https://branch.nour.example",
    "http://localhost:5173",
]

PROBLEM_CONTENT_TYPE = "application/problem+json"


def _problem(status_code: int, detail: str, instance: str, type_: str = "about:blank"):
    return JSONResponse(
        status_code=status_code,
        media_type=PROBLEM_CONTENT_TYPE,
        content={
            "type": type_,
            "title": detail,
            "status": status_code,
            "detail": detail,
            "instance": instance,
        },
    )


def create_app(stock, items, sales, now):
    """Create a FastAPI app with the given state.

    stock: dict branch -> item_code -> int
    items: dict item_code -> dict(chronic bool, reserve int)
    sales: dict branch -> item_code -> float
    now: callable returning current UTC datetime
    """
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    transfers = {}  # transfer id -> record
    next_id = [1]

    class TransferRequest(BaseModel):
        fromBranch: str
        toBranch: str
        itemCode: str
        quantity: int = Field(ge=1)
        memo: Optional[str] = None

    @app.get("/v1/branches/{branch}/stock/{item_code}")
    def get_stock(branch: str, item_code: str):
        if branch not in stock or item_code not in stock.get(branch, {}):
            return _problem(status.HTTP_404_NOT_FOUND, "Unknown branch or item",
                            f"/v1/branches/{branch}/stock/{item_code}")
        return {
            "branch": branch,
            "itemCode": item_code,
            "stock": stock[branch][item_code],
            "reserve": items[item_code]["reserve"],
            "chronic": items[item_code]["chronic"],
            "avgDailySales": sales.get(branch, {}).get(item_code, 0.0),
        }

    @app.post("/v1/transfers")
    async def create_transfer(request: Request):
        body = await request.json()
        try:
            req = TransferRequest(**body)
        except Exception:
            return _problem(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Validation error", "/v1/transfers")

        if req.fromBranch == req.toBranch:
            return _problem(status.HTTP_409_CONFLICT, "Same branch transfer",
                            "/v1/transfers", type_="/problems/same-branch")

        if req.fromBranch not in stock or req.toBranch not in stock:
            return _problem(status.HTTP_404_NOT_FOUND, "Unknown branch",
                            "/v1/transfers")

        if req.itemCode not in items:
            return _problem(status.HTTP_404_NOT_FOUND, "Unknown item",
                            "/v1/transfers")

        item = items[req.itemCode]
        from_stock = stock.get(req.fromBranch, {}).get(req.itemCode, 0)

        if not rules.can_transfer(from_stock, req.quantity, item["reserve"]):
            return _problem(status.HTTP_409_CONFLICT, "Below reserve",
                            "/v1/transfers", type_="/problems/below-reserve")

        cover = rules.days_of_cover(
            stock.get(req.toBranch, {}).get(req.itemCode, 0),
            sales.get(req.toBranch, {}).get(req.itemCode, 0.0),
        )
        prio = rules.priority(item["chronic"], cover)

        tid = f"T{next_id[0]:04d}"
        next_id[0] += 1

        record = {
            "id": tid,
            "itemCode": req.itemCode,
            "fromBranch": req.fromBranch,
            "toBranch": req.toBranch,
            "quantity": req.quantity,
            "requestedAt": now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": "pending",
            "priority": prio,
            "reserve": item["reserve"],
            "memo": req.memo,
        }
        transfers[tid] = record
        return JSONResponse(status_code=status.HTTP_201_CREATED,
                            content=record)

    @app.post("/v1/transfers/{transfer_id}/approve")
    async def approve_transfer(transfer_id: str):
        if transfer_id not in transfers:
            return _problem(status.HTTP_404_NOT_FOUND, "Unknown transfer",
                            f"/v1/transfers/{transfer_id}/approve")

        record = transfers[transfer_id]
        if record["status"] != "pending":
            return _problem(status.HTTP_409_CONFLICT, "Not pending",
                            f"/v1/transfers/{transfer_id}/approve",
                            type_="/problems/not-pending")

        from_stock = stock.get(record["fromBranch"], {}).get(record["itemCode"], 0)
        if from_stock < record["quantity"] + items[record["itemCode"]]["reserve"]:
            return _problem(status.HTTP_409_CONFLICT, "Below reserve",
                            f"/v1/transfers/{transfer_id}/approve",
                            type_="/problems/below-reserve")

        stock[record["fromBranch"]][record["itemCode"]] -= record["quantity"]
        stock[record["toBranch"]][record["itemCode"]] = (
            stock.get(record["toBranch"], {}).get(record["itemCode"], 0) + record["quantity"]
        )
        record["status"] = "approved"
        return record

    @app.get("/v1/branches/{branch}/transfers")
    def get_inbox(branch: str):
        inbox = [r for r in transfers.values() if r["toBranch"] == branch]
        order = {"urgent": 0, "high": 1, "normal": 2}
        inbox.sort(key=lambda r: (order.get(r["priority"], 3), r["requestedAt"]))
        return {"items": inbox}

    return app