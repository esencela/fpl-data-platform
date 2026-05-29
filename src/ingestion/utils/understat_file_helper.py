import os
from pathlib import Path
from datetime import datetime
import json
from src.config.settings import settings
from src.ingestion.utils.file_utils import get_latest_file_for_each_season, get_latest_path

UNDERSTAT_DATA_DIR = settings.RAW_DATA_DIR / 'understat'

def get_latest_season_files() -> list[Path]:
    """Returns a list of paths to the latest raw season JSON files."""

    season_dir = UNDERSTAT_DATA_DIR / 'season_data'

    return get_latest_file_for_each_season(season_dir, '.json')


def get_latest_match_files() -> list[tuple[str, str]]:
    """Returns a list of tuples containing match IDs and JSON data for all match data files."""

    match_data_dir = UNDERSTAT_DATA_DIR / 'matches'

    match_files = []

    for file in match_data_dir.glob('match_id=*.json'):
        match_id = file.stem.split('=')[1]

        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            match_files.append((match_id, json.dumps(data)))

    return match_files


def get_latest_id_mappings_file() -> Path:
    """Returns the path to the most recent player and team ID mappings Parquet file."""

    id_mappings_dir = UNDERSTAT_DATA_DIR / 'id_mappings'

    files = list(id_mappings_dir.glob('*.parquet'))

    if not files:
        raise FileNotFoundError(f'No ID mappings files found in {id_mappings_dir}')

    return max(files)