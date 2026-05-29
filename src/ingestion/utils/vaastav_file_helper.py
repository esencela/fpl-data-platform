import os
from pathlib import Path
from datetime import datetime
from src.ingestion.utils.file_utils import get_latest_file_for_each_season

RAW_DATA_DIR = os.getenv('RAW_DATA_DIR', '/app/data/raw/vaastav')

def get_latest_player_files() -> list[Path]:
    """Returns a list of paths to the latest player parquet files."""

    player_dir = RAW_DATA_DIR / 'players'

    return get_latest_file_for_each_season(player_dir, '.parquet')


def get_latest_gameweek_files() -> list[Path]:
    """Returns a list of paths to the latest player parquet files."""

    gw_dir = RAW_DATA_DIR / 'gws'

    return get_latest_file_for_each_season(gw_dir, '.parquet')


def get_latest_fixture_files() -> list[Path]:
    """Returns a list of paths to the latest raw fixture parquet files."""

    fixture_dir = RAW_DATA_DIR / 'fixtures'

    return get_latest_file_for_each_season(fixture_dir, '.parquet')


def get_latest_team_files() -> list[Path]:
    """Returns a list of paths to the latest raw team parquet files."""

    team_dir = RAW_DATA_DIR / 'teams'

    return get_latest_file_for_each_season(team_dir, '.parquet')