from __future__ import annotations
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "sqlite:///./gcmrp.db"
    default_commodities: list[str] = ["wheat", "coffee", "sugar"]

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> "Settings":
    s = Settings()
    if isinstance(s.default_commodities, str):
        s.default_commodities = [c.strip() for c in s.default_commodities.split(",") if c.strip()]
    return s

