run-api:
	uvicorn gcmrp.api.main:app --reload
seed:
	python -m gcmrp.jobs.backfill --commodities wheat coffee sugar --days 90

