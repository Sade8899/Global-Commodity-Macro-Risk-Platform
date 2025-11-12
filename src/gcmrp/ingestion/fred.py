from __future__ import annotations
import os
import requests
import pandas as pd
from datetime import datetime

FRED_API_KEY = os.getenv("FRED_API_KEY", "879039fa349e8ede599d9981b671b192")
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

FRED_SERIES = {
    "wheat": "PWHEAMTUSDM",
    "coffee": "PCOFFOTMUSDM",
    "cocoa": "PCOCOUSDM"
}

def fetch_fred_series(commodity: str, start_date: str = "2000-01-01") -> pd.DataFrame:
    if commodity not in FRED_SERIES:
        raise ValueError(f"Unsupported commodity: {commodity}")
    series_id = FRED_SERIES[commodity]
    params = {
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "series_id": series_id,
        "observation_start": start_date
    }
    r = requests.get(FRED_BASE_URL, params=params)
    r.raise_for_status()
    obs = r.json()["observations"]
    df = pd.DataFrame(obs)
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])
    df = df.rename(columns={"value": "close"})
    return df[["date", "close"]]

