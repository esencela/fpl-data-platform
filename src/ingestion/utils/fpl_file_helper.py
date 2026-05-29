import json
from pathlib import Path
from config.settings import settings
from ingestion.utils.file_utils import get_latest_path, get_latest_season_folder

FPL_DATA_DIR = settings.RAW_DATA_DIR / 'fpl'


def get_latest_bootstrap_file() -> Path:
    """Returns the path to the most recent bootstrap JSON file."""

    bootstrap_dir = FPL_DATA_DIR / 'bootstrap-static'

    return get_latest_path(bootstrap_dir, '.json')


def get_latest_element_summaries() -> list[tuple[int, int, str, str]]:
    """Returns a list of records from the most recent element summary JSON files."""
    
    element_summary_dir = FPL_DATA_DIR / 'element-summary'

    latest_fetch = get_latest_path(element_summary_dir)
    season = int(latest_fetch.parent.name.split('=')[1])
    latest_date = latest_fetch.stem

    elements = []
    for file in latest_fetch.glob('*.json'):
        player_id = int(file.stem.split('=')[1])
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            elements.append((season, player_id, json.dumps(data), latest_date))

    return elements


def get_latest_fixtures_file() -> Path:
    """Returns the path to the most recent fixtures JSON file."""

    fixtures_dir = FPL_DATA_DIR / 'fixtures'

    return get_latest_path(fixtures_dir, '.json')


def get_latest_events() -> list[tuple[int, int, str, str]]:
    """Returns a list of records from the most recent events JSON files."""
    
    events_dir = FPL_DATA_DIR / 'events'

    latest_fetch = get_latest_path(events_dir)
    season = int(latest_fetch.parent.name.split('=')[1])
    latest_date = latest_fetch.stem

    elements = []
    for file in latest_fetch.glob('*.json'):
        gameweek_id = int(file.stem.split('=')[1])
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            elements.append((season, gameweek_id, json.dumps(data), latest_date))

    return elements