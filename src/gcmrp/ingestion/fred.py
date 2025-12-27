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

def fetch_fred_series(
    commodity: str,
    start_date: str = '2000-01-01',
    *,
    series_id: str | None = None,
    frequency: str | None = None,            # 'd','w','m','q','a' (must not exceed original series frequency)
    aggregation_method: str = 'eop'          # for frequency conversion
) -> pd.DataFrame:
    """Fetch a FRED series for a commodity.

    If the original series is monthly, setting frequency='d' does NOT create true daily data;
    FRED will only convert frequency (e.g., step-style values using aggregation_method).
    For real daily data, pass a true daily series_id via --series-overrides.
    """
    if commodity not in FRED_SERIES and not series_id:
        raise ValueError(f'Unsupported commodity: {commodity}')
    sid = series_id or FRED_SERIES[commodity]

    params = {
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'series_id': sid,
        'observation_start': start_date,
    }
    if frequency:
        params['frequency'] = frequency
        if aggregation_method:
            params['aggregation_method'] = aggregation_method

    r = requests.get(FRED_BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    obs = r.json().get('observations', [])
    df = pd.DataFrame(obs)
    if df.empty:
        return pd.DataFrame(columns=['date','close'])
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df = df.dropna(subset=['value']).rename(columns={'value': 'close'})
    return df[['date','close']]

from gcmrp.config import get_settings
FRED_API_KEY = os.getenv("FRED_API_KEY") or (get_settings().fred_api_key or "")

