# Global-Commodity-Macro-Risk-Platform (skeleton)

Quickstart skeleton for a Python backend that ingests commodity price data,
stores it (SQLite/Postgres), computes basic analytics, and exposes a tiny API.

## Quickstart
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
python -m gcmrp.jobs.backfill --commodities wheat coffee sugar --days 90
uvicorn gcmrp.api.main:app --reload

