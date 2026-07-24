from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Configuration settings for the FPL data platform."""

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # Current season - e.g. 2026 for the 2025/26 season
    CURRENT_SEASON: int = 2027

    RAW_DATA_DIR: Path = Path('/tmp/fpl_data')

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int = 5432

settings = Settings()