import argparse
import os
import sys
from pathlib import Path

# Allow running this file directly without installing the package.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gcmrp.ingestion.fred import fetch_fred_series

def test_fred_fetch_print(commodities=("wheat","coffee","cocoa"), last_n=5, start_date="2000-01-01"):
    print("\n?? FRED API Test - Last records per commodity\n")
    print(f"FRED_API_KEY present: {bool(os.getenv('FRED_API_KEY'))}")
    print(f"Start date: {start_date} | Showing last {last_n}\n")
    for commodity in commodities:
        try:
            df = fetch_fred_series(commodity, start_date=start_date)
            print(f"?? {commodity.title()} - {len(df)} records total")
            print(df.tail(last_n).to_string(index=False))
            print()
        except Exception as e:
            print(f"? Error fetching {commodity}: {e}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commodities", nargs="+", default=["wheat","coffee","cocoa"])
    ap.add_argument("--last", type=int, default=5)
    ap.add_argument("--start-date", default="2000-01-01")
    args = ap.parse_args()
    test_fred_fetch_print(tuple(args.commodities), last_n=args.last, start_date=args.start_date)

if __name__ == "__main__":
    main()
