from __future__ import annotations
from datetime import date, timedelta
import random
import pandas as pd


def fetch_price_data_stub(symbol: str, days: int = 90) -> pd.DataFrame:
    random.seed(symbol)
    base = 100 + sum(ord(c) for c in symbol) % 50
    dates = [date.today() - timedelta(days=i) for i in range(days)][::-1]
    prices, level = [], base
    for _ in dates:
        level *= 1 + random.uniform(-0.01, 0.01)
        prices.append(round(level, 2))
    return pd.DataFrame({"date": dates, "close": prices})

