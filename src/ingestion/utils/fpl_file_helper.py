import json
from pathlib import Path
from config.settings import settings
from ingestion.utils.file_utils import get_latest_path, get_latest_path_for_season

FPL_DATA_DIR = settings.RAW_DATA_DIR / 'fpl'


def get_latest_bootstrap_file(season: int = None) -> Path:
    """Returns the path to the most recent bootstrap JSON file."""

    bootstrap_dir = FPL_DATA_DIR / 'bootstrap-static'

    if season is not None:
        return get_latest_path_for_season(bootstrap_dir, season, '.json')
    else:
        return get_latest_path(bootstrap_dir, '.json')


def get_latest_element_summaries(season: int = None) -> list[tuple[int, int, str, str]]:
    """Returns a list of records from the most recent element summary JSON files."""
    
    element_summary_dir = FPL_DATA_DIR / 'element-summary'

    if season is not None:
        latest_fetch = get_latest_path_for_season(element_summary_dir, season)
    else:
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


def get_latest_fixtures_file(season: int = None) -> Path:
    """Returns the path to the most recent fixtures JSON file."""

    fixtures_dir = FPL_DATA_DIR / 'fixtures'

    if season is not None:
        return get_latest_path_for_season(fixtures_dir, season, '.json')
    else:
        return get_latest_path(fixtures_dir, '.json')


def get_latest_events(season: int = None) -> list[tuple[int, int, str, str]]:
    """Returns a list of records from the most recent events JSON files."""
    
    events_dir = FPL_DATA_DIR / 'events'

    if season is not None:
        latest_fetch = get_latest_path_for_season(events_dir, season)
    else:
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


def get_available_seasons() -> list[int]:
    """Returns a list of available seasons based on FPL directory structure"""

    bootstrap_dir = FPL_DATA_DIR / 'bootstrap-static'
    seasons = [int(path.name.split('=')[1]) for path in bootstrap_dir.glob('season=*') if path.is_dir()]
    
    return sorted(seasons)