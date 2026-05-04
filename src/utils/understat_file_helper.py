from pathlib import Path
from datetime import datetime
from src.utils.file_utils import get_latest_file_for_each_season

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / 'data' / 'raw' / 'understat'


def get_latest_team_files() -> list[Path]:
    """Returns a list of paths to the latest raw team JSON files."""

    team_dir = RAW_DATA_DIR / 'team_data'

    return get_latest_file_for_each_season(team_dir, '.json')