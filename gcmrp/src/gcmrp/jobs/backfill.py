from __future__ import annotations
import argparse
from gcmrp.db.base import SessionLocal, init_db
from gcmrp.db.models import Commodity, Price
from gcmrp.ingestion.pipeline import fetch_price_data_stub


def ensure_commodity(db, symbol: str, name: str | None = None):
    c = db.query(Commodity).filter(Commodity.symbol == symbol).first()
    if c:
        return c
    c = Commodity(symbol=symbol, name=name or symbol.title())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def main():
    ap = argparse.ArgumentParser(description="Seed DB with synthetic price data (stub)")
    ap.add_argument("--commodities", nargs="+", default=["wheat", "coffee", "sugar"])
    ap.add_argument("--days", type=int, default=90)
    args = ap.parse_args()

    init_db()
    db = SessionLocal()
    try:
        for sym in args.commodities:
            c = ensure_commodity(db, sym)
            df = fetch_price_data_stub(sym, days=args.days)
            for row in df.to_dict(orient="records"):
                exists = (
                    db.query(Price)
                    .filter(Price.commodity_id == c.id, Price.date == row["date"])
                    .first()
                )
                if not exists:
                    db.add(Price(commodity_id=c.id, date=row["date"], close=float(row["close"])))
            db.commit()
        print("Backfill complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

