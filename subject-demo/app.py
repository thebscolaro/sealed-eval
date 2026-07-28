"""Tiny subject app for sealed-eval demo."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="subject-demo-orders")
_ORDERS: dict[str, dict] = {}
_SEQ = 0


class OrderIn(BaseModel):
    sku: str
    qty: int


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/orders", status_code=201)
def create(order: OrderIn):
    global _SEQ
    if order.qty < 1:
        raise HTTPException(400, "qty")
    _SEQ += 1
    oid = str(_SEQ)
    row = {"id": oid, "sku": order.sku, "qty": order.qty}
    _ORDERS[oid] = row
    return row


@app.get("/orders/{oid}")
def get(oid: str):
    if oid not in _ORDERS:
        raise HTTPException(404, "missing")
    return _ORDERS[oid]
