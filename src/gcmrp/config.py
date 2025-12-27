from __future__ import annotations
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./gcmrp.db"
    default_commodities: List[str] = ["wheat", "coffee", "sugar"]
    fred_api_key: Optional[str] = None  # read from .env if present
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # ignore unrelated keys like PYTHONPATH, etc.
    )

@lru_cache
def get_settings() -> "Settings":
    s = Settings()
    if isinstance(s.default_commodities, str):
        s.default_commodities = [c.strip() for c in s.default_commodities.split(",") if c.strip()]
    return s
