import understatapi
from datetime import datetime
from pathlib import Path
import time
import logging
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / 'data' / 'raw' / 'understat'

CURRENT_DATE = datetime.now().strftime('%Y-%m-%d')
MIN_SEASON = 2017
CURRENT_SEASON = 2026

RATE_LIMIT = 0.5 # seconds between requests to avoid hitting API rate limits

logger = logging.getLogger(__name__)

client = understatapi.UnderstatClient()

def get_understat_season(season: int) -> str:
    """Understat uses first year of season as string to identify season, e.g. '2025' for 2025-26 season."""
    return str(season - 1)


def extract_team_data() -> None:
    """Extracts team data for all seasons from Understat and saves to JSON file."""

    logger.info('Extracting team data from Understat...')

    for season in range(MIN_SEASON, CURRENT_SEASON + 1):
        season_str = get_understat_season(season)

        try:
            team_data = client.league('EPL').get_team_data(season_str)
        
        except Exception as e:
            logger.error(f'Failed to extract team data for season {season}: {e}')
            raise Exception(f'Failed to extract team data for season {season}: {e}')
        
        if team_data == []:
            logger.warning(f'No team data found for season {season}. Skipping...')
            continue

        # Save the extracted data to a JSON file named with the current date
        file_path = RAW_DATA_DIR / 'team_data' / f'season={season}' / f'{CURRENT_DATE}.json'
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(team_data, file, indent=4, ensure_ascii=False)

        logger.info(f'Team data for season {season} saved to {file_path}')

        time.sleep(RATE_LIMIT)