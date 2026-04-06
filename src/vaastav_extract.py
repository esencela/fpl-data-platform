import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
from src.config import CURRENT_SEASON

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / 'data' / 'raw' / 'vaastav'

CURRENT_DATE = datetime.now().strftime('%Y-%m-%d')
MIN_SEASON = 2017

logger = logging.getLogger(__name__)

def get_season_string(season: int) -> str:
    """Converts a season integer (e.g. 2026) to a string format used in file paths (e.g. '2025-26')."""
    start_year = season - 1

    return f'{start_year}-{str(season)[-2:]}'

seasons = [(get_season_string(season), season) for season in range(MIN_SEASON, 2026)] # Extraction of FPL API data starts from 25/26 season, we only need historic data up to 24/25 season


def extract_player_data() -> None:
    """Extracts raw player CSV files from GitHub and saves them as Parquet files."""    

    for season_string, season in seasons:
        base_url = f'https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/{season_string}/'

        base_path = RAW_DATA_DIR / 'players' / f'season={season}'

        # Raw player data
        player_url = base_url + 'players_raw.csv'
        player_df = pd.read_csv(player_url)

        file_path = base_path / f'{CURRENT_DATE}.parquet'
        file_path.parent.mkdir(parents=True, exist_ok=True)
        player_df.to_parquet(file_path, index=False)
        logger.info(f'Player data for season {season} extracted and saved to {file_path}')


