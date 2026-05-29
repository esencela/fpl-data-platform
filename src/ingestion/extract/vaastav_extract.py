import pandas as pd
from pathlib import Path
from datetime import datetime
from urllib.error import HTTPError
import logging
from src.config.settings import settings

VAASTAV_DATA_DIR = settings.RAW_DATA_DIR / 'vaastav'

CURRENT_DATE = datetime.now().strftime('%Y-%m-%d')
MIN_SEASON = 2017
MAX_SEASON = 2025

logger = logging.getLogger(__name__)


def get_season_string(season: int) -> str:
    """Converts a season integer (e.g. 2026) to a string format used in file paths (e.g. '2025-26')."""
    start_year = season - 1

    return f'{start_year}-{str(season)[-2:]}'


seasons = [(get_season_string(season), season) for season in range(MIN_SEASON, MAX_SEASON + 1)] # Extraction of FPL API data starts from 25/26 season, we only need historic data up to 24/25 season
base_url = f'https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/'


def extract_player_data() -> None:
    """Extracts raw player CSV files from GitHub and saves as parquet files."""  

    logger.info('Extracting player data from GitHub...')  

    for season_string, season in seasons:
        base_path = VAASTAV_DATA_DIR / 'players' / f'season={season}'

        # Raw player data
        player_url = base_url + f'{season_string}/players_raw.csv'

        try:
            df_player = pd.read_csv(player_url)

            file_path = base_path / f'{CURRENT_DATE}.parquet'
            file_path.parent.mkdir(parents=True, exist_ok=True)
            df_player.to_parquet(file_path, index=False)

            logger.info(f'Player data for season {season} extracted and saved to {file_path}')
        
        except Exception as e:
            logger.error(f'Failed to retrieve player data: {e}')
            raise


def extract_gameweek_data() -> None:
    """Extracts raw player-game CSV files from GitHub and saves as parquet files."""

    logger.info('Extracting player-game data from GitHub...')  

    for season_string, season in seasons:
        base_path = VAASTAV_DATA_DIR / 'gws' / f'season={season}'

        # Raw player-game data
        gw_url = base_url + f'{season_string}/gws/merged_gw.csv'

        try:
            df_gw = pd.read_csv(gw_url, encoding='latin-1') # utf-8 fails so use latin-1 for github data

            file_path = base_path / f'{CURRENT_DATE}.parquet'
            file_path.parent.mkdir(parents=True, exist_ok=True)
            df_gw.to_parquet(file_path, index=False)

            logger.info(f'Player-Game data for season {season} extracted and saved to {file_path}')

        except Exception as e:
            logger.error(f'Failed to retrieve player-game data: {e}')
            raise


def extract_fixture_data() -> None:
    """Extracts raw fixture CSV files from GitHub and saves as parquet files."""

    logger.info('Extracting fixture data from GitHub...')

    for season_string, season in seasons:
        base_path = VAASTAV_DATA_DIR / 'fixtures' / f'season={season}'

        # Raw fixture data
        fixture_url = base_url + f'{season_string}/fixtures.csv'

        try:
            df_fixtures = pd.read_csv(fixture_url)

            file_path = base_path / f'{CURRENT_DATE}.parquet'
            file_path.parent.mkdir(parents=True, exist_ok=True)
            df_fixtures.to_parquet(file_path, index=False)

            logger.info(f'Fixture data for season {season} extracted and saved to {file_path}')

        except HTTPError as e: 
            if e.code == 404:                
                logger.warning(f'Fixture data not available for {season} season')
            else:
                logger.error(f'Failed to retrieve fixture data: {e}')
                raise
        except Exception as e:
            logger.error(f'Failed to retrieve fixture data: {e}')
            raise


def extract_team_data() -> None:
    """Extracts raw team csv files from GitHub and saves as parquet files"""

    logger.info('Extracting team data from GitHub...')

    for season_string, season in seasons:
        base_path = VAASTAV_DATA_DIR / 'teams' / f'season={season}'

        # Raw team data
        team_url = base_url + f'{season_string}/teams.csv'

        try:
            df_team = pd.read_csv(team_url)

            file_path = base_path / f'{CURRENT_DATE}.parquet'
            file_path.parent.mkdir(parents=True, exist_ok=True)
            df_team.to_parquet(file_path, index=False)

            logger.info(f'Team data for season {season} extracted and saved to {file_path}')

        except HTTPError as e:
            if e.code == 404:
                logger.warning(f'Team data not available for {season} season')
            else:
                logger.error(f'Failed to retrieve team data: {e}')
                raise
        except Exception as e:
            logger.error(f'Failed to retrieve team data: {e}')
            raise


extract_player_data()
extract_gameweek_data()
extract_fixture_data()
extract_team_data()