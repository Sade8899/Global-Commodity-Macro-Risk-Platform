from __future__ import annotations
import argparse
from datetime import date
from sqlalchemy.orm import Session
from gcmrp.db.base import SessionLocal, init_db
from gcmrp.db.models import Commodity, Price
from gcmrp.ingestion.fred import fetch_fred_series

def ensure_commodity(db: Session, symbol: str, name: str | None = None) -> Commodity:
    c = db.query(Commodity).filter(Commodity.symbol == symbol).first()
    if c: return c
    c = Commodity(symbol=symbol, name=name or symbol.title())
    db.add(c); db.commit(); db.refresh(c)
    return c

def upsert_prices(db: Session, commodity: Commodity, start_date: str = '2000-01-01', *, series_id: str | None = None, frequency: str | None = None) -> int:
    df = fetch_fred_series(commodity.symbol, start_date=start_date, series_id=series_id, frequency=frequency)
    count = 0
    for row in df.itertuples(index=False):
        d = row.date.date() if hasattr(row.date, 'date') else row.date
        exists = (db.query(Price)
                    .filter(Price.commodity_id == commodity.id, Price.date == d)
                    .first())
        if exists:
            if exists.close != float(row.close):
                exists.close = float(row.close)
        else:
            db.add(Price(commodity_id=commodity.id, date=d, close=float(row.close)))
            count += 1
    db.commit()
    return count

def main():
    ap = argparse.ArgumentParser(description='Ingest FRED prices into DB (supports daily via series overrides).')
    ap.add_argument('--commodities', nargs='+', default=['wheat','coffee','cocoa'])
    ap.add_argument('--start-date', default='2000-01-01')
    args = ap.parse_args()

    init_db()
    db = SessionLocal()
    try:
        for sym in args.commodities:
            c = ensure_commodity(db, sym)
            # parse overrides: 'wheat=XXXX,coffee=YYYY'
            overrides = {}
            if args.series_overrides:
                for kv in args.series_overrides.split(','):
                    if '=' in kv:
                        k, v = kv.split('=', 1)
                        overrides[k.strip()] = v.strip()
            sid = overrides.get(sym)
            added = upsert_prices(db, c, start_date=args.start_date, series_id=sid, frequency=args.frequency)
            print(f'[INGEST] {sym}: upserted {added} new rows')
    finally:
        db.close()

if __name__ == '__main__':
    main()

