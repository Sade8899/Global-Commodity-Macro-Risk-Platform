from gcmrp.ingestion.fred import fetch_fred_series
df = fetch_fred_series("cocoa")
print(df.tail())

