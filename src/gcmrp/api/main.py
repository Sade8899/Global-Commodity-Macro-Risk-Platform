from __future__ import annotations
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta, date, timedelta
from gcmrp.db.base import SessionLocal, init_db
from gcmrp.db.models import Commodity, Price


app = FastAPI(title="GCMRP API")



# CORS (dev-open; tighten for prod)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
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

from gcmrp.analytics.volatility import rolling_volatility
import pandas as pd

@app.get('/analytics/volatility/{symbol}')
def get_volatility(symbol: str, window: int = 30, db: Session = Depends(get_db)):
    c = db.query(Commodity).filter(Commodity.symbol == symbol).first()
    if not c:
        raise HTTPException(status_code=404, detail='Commodity not found')
    rows = (db.query(Price)
              .filter(Price.commodity_id == c.id)
              .order_by(Price.date.asc())
              .all())
    if not rows:
        return {'symbol': symbol, 'window': window, 'values': []}
    df = pd.DataFrame([{'date': r.date, 'close': r.close} for r in rows])
    vol = rolling_volatility(df, window=window).reset_index()
    vol.columns = ['index', 'value']
    return {
        'symbol': symbol,
        'window': window,
        'values': [{'date': df.loc[i, 'date'].isoformat(), 'vol': float(v)}
                   for i, v in zip(vol['index'], vol['value']) if pd.notna(v)][-120:]
    }

from fastapi.staticfiles import StaticFiles
app.mount('/dash', StaticFiles(directory='frontend', html=True), name='dash')

from fastapi.responses import RedirectResponse

@app.get("/")
def root():
    return RedirectResponse(url="/dash/", status_code=307)
@app.get("/api/dash-data/{symbol}")
def dash_data(symbol: str, window: int = 30, days: int = 365, db: Session = Depends(get_db)):
    # Validate commodity
    c = db.query(Commodity).filter(Commodity.symbol == symbol).first()
    if not c:
        raise HTTPException(status_code=404, detail="Commodity not found")
    # Load prices (ASC) within window
    cutoff = date.today() - timedelta(days=days)
    rows = (db.query(Price)
              .filter(Price.commodity_id == c.id, Price.date >= cutoff)
              .order_by(Price.date.asc())
              .all())
    prices = [{"date": r.date.isoformat(), "close": float(r.close)} for r in rows]
    # Rolling volatility (simple pct-change rolling std)
    vol_values = []
    if prices:
        df = pd.DataFrame(prices)
        df["ret"] = df["close"].pct_change()
        df["vol"] = df["ret"].rolling(window).std()
        for i, row in df.iterrows():
            if pd.notna(row["vol"]):
                vol_values.append({"date": str(row["date"])[:10], "vol": float(row["vol"])})
    return {"symbol": symbol, "prices": prices, "vol": vol_values}




@app.get("/api/dash-data-multi")
def dash_data_multi(symbols: str, window: int = 30, days: int = 365, db: Session = Depends(get_db)):
    # symbols: comma-separated e.g. "wheat,coffee,cocoa"
    syms = [s.strip() for s in symbols.split(",") if s.strip()]
    out = {}
    cutoff = date.today() - timedelta(days=days)
    for sym in syms:
        c = db.query(Commodity).filter(Commodity.symbol == sym).first()
        if not c:
            out[sym] = {"prices": [], "vol": []}
            continue
        rows = (
            db.query(Price)
            .filter(Price.commodity_id == c.id, Price.date >= cutoff)
            .order_by(Price.date.asc())
            .all()
        )
        prices = [{"date": r.date.isoformat(), "close": float(r.close)} for r in rows]
        vol_values = []
        if prices:
            df = pd.DataFrame(prices)
            df["ret"] = df["close"].pct_change()
            df["vol"] = df["ret"].rolling(window).std()
            for _, r in df.iterrows():
                if pd.notna(r["vol"]):
                    vol_values.append({"date": str(r["date"])[:10], "vol": float(r["vol"])})
        out[sym] = {"prices": prices, "vol": vol_values}
    return out
