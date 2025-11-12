from __future__ import annotations
import pandas as pd


def rolling_volatility(df: pd.DataFrame, window: int = 30):
    returns = df["close"].pct_change()
    return returns.rolling(window=window, min_periods=window // 2).std()

