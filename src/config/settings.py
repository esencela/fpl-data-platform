from dataclasses import dataclass
import os
from pathlib import Path

@dataclass
class Settings:
    """Configuration settings for the FPL data platform."""

    # Current season - e.g. 2026 for the 2025/26 season
    CURRENT_SEASON: int = 2026

    RAW_DATA_DIR: Path = Path(os.getenv('RAW_DATA_DIR'))

    postgres_db: str = os.getenv('POSTGRES_DB')
    postgres_user: str = os.getenv('POSTGRES_USER')
    postgres_password: str = os.getenv('POSTGRES_PASSWORD')
    postgres_host: str = os.getenv('POSTGRES_HOST')
    postgres_port: int = int(os.getenv('POSTGRES_PORT'))

settings = Settings()