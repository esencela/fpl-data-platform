from pathlib import Path
from datetime import datetime
from src.utils.file_utils import get_latest_file_for_each_season

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / 'data' / 'raw' / 'understat'


def get_latest_season_files() -> list[Path]:
    """Returns a list of paths to the latest raw season JSON files."""

    season_dir = RAW_DATA_DIR / 'season_data'

    return get_latest_file_for_each_season(season_dir, '.json')