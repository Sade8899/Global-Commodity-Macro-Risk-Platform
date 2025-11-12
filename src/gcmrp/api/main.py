from __future__ import annotations
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from gcmrp.db.base import SessionLocal, init_db
from gcmrp.db.models import Commodity, Price


app = FastAPI(title="GCMRP API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def _startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/commodities")
def list_commodities(db: Session = Depends(get_db)):
    rows = db.query(Commodity).all()
    return [{"symbol": c.symbol, "name": c.name} for c in rows]


@app.get("/prices/{symbol}")
def get_prices(symbol: str, days: int = 90, db: Session = Depends(get_db)):
    c = db.query(Commodity).filter(Commodity.symbol == symbol).first()
    if not c:
        raise HTTPException(status_code=404, detail="Commodity not found")
    since = date.today() - timedelta(days=days)
    prices = (
        db.query(Price)
        .filter(Price.commodity_id == c.id, Price.date >= since)
        .order_by(Price.date.asc())
        .all()
    )
    return [{"date": p.date.isoformat(), "close": p.close} for p in prices]

