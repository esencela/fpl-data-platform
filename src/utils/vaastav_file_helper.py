from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / 'data' / 'raw' / 'vaastav'


def get_latest_player_files() -> list[Path]:
    """Returns a list of paths to the latest player parquet files."""

    player_dir = RAW_DATA_DIR / 'players'

    # for each season folder, get the most recent parquet file
    latest_files = []
    for season_folder in player_dir.glob('season=*'):
        file_list = list(season_folder.glob('*.parquet'))

        if not file_list:
            raise FileNotFoundError(f'No player files found in {season_folder}')
        
        latest_file = max(file_list)
        latest_files.append(latest_file)

    return latest_files


def get_latest_gameweek_files() -> list[Path]:
    """Returns a list of paths to the latest player parquet files."""

    gw_dir = RAW_DATA_DIR / 'gws'

    # for each season folder, get the most recent parquet file
    latest_files = []
    for season_folder in gw_dir.glob('season=*'):
        file_list = list(season_folder.glob('*.parquet'))

        if not file_list:
            raise FileNotFoundError(f'No player files found in {season_folder}')
        
        latest_file = max(file_list)
        latest_files.append(latest_file)

    return latest_files


def get_latest_fixture_files() -> list[Path]:
    """Returns a list of paths to the latest raw fixture parquet files."""

    fixture_dir = RAW_DATA_DIR / 'fixtures'

    latest_files = []

    # for each season folder, get the most recent parquet file
    for season_folder in fixture_dir.glob('season=*'):
        file_list = list(season_folder.glob('*.parquet'))

        if not file_list:
            raise FileNotFoundError(f'No fixture files found in {season_folder}')
        
        latest_file = max(file_list)
        latest_files.append(latest_file)

    return latest_files


def get_latest_team_files() -> list[Path]:
    """Returns a list of paths to the latest raw team parquet files."""

    team_dir = RAW_DATA_DIR / 'teams'

    latest_files = []

    for season_folder in team_dir.glob('season=*'):
        file_list = list(season_folder.glob('*.parquet'))

        if not file_list:
            raise FileNotFoundError(f'No team files found in {season_folder}')
        
        latest_file = max(file_list)
        latest_files.append(latest_file)

    return latest_files