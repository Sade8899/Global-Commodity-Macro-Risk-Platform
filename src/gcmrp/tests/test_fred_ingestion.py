import os
import argparse
from gcmrp.ingestion.fred import fetch_fred_series

def test_fred_fetch_print(commodities=("wheat", "coffee", "cocoa"), last_n=5, start_date="2000-01-01"):
    """
    Prints the last N rows for each commodity from FRED.
    Keeps pytest-friendly signature, but you can call it directly too.
    """
    print("\n🟢 FRED API Test — Last records per commodity\n")
    print(f"FRED_API_KEY present: {bool(os.getenv('FRED_API_KEY'))}")
    print(f"Start date: {start_date} | Showing last {last_n}\n")

    for commodity in commodities:
        try:
            df = fetch_fred_series(commodity, start_date=start_date)
            print(f"🔸 {commodity.title()} — {len(df)} records total")
            print(df.tail(last_n).to_string(index=False))
            print()
        except Exception as e:
            print(f"❌ Error fetching {commodity}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Print FRED series for selected commodities.")
    parser.add_argument(
        "--commodities",
        nargs="+",
        default=["wheat", "coffee", "cocoa"],
        help="List of commodities to fetch (default: wheat coffee cocoa)",
    )
    parser.add_argument(
        "--last",
        type=int,
        default=5,
        help="Show the last N rows (default: 5)",
    )
    parser.add_argument(
        "--start-date",
        default="2000-01-01",
        help="Observation start date (YYYY-MM-DD, default: 2000-01-01)",
    )
    args = parser.parse_args()

    # run the same logic used by the pytest-style function
    test_fred_fetch_print(tuple(args.commodities), last_n=args.last, start_date=args.start_date)

if __name__ == "__main__":
    main()
