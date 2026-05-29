import understatapi
from datetime import datetime
from pathlib import Path
import pandas as pd
import time
import logging
import json
import asyncio
import os
from src.ingestion.utils.understat_file_helper import get_latest_season_files
from src.config.settings import settings

UNDERSTAT_DATA_DIR = settings.RAW_DATA_DIR / 'understat'

CURRENT_DATE = datetime.now().strftime('%Y-%m-%d')
MIN_SEASON = 2017
CURRENT_SEASON = 2026

RATE_LIMIT = 0.1 # seconds between requests to avoid hitting API rate limits

logger = logging.getLogger(__name__)

client = understatapi.UnderstatClient()


def get_understat_season(season: int) -> str:
    """Understat uses first year of season as string to identify season, e.g. '2025' for 2025-26 season."""
    return str(season - 1)


def extract_season_data() -> None:
    """Extracts season data including team, player, and match data for all seasons from Understat and saves to JSON file."""

    logger.info('Extracting season data from Understat...')

    for season in range(MIN_SEASON, CURRENT_SEASON + 1):
        season_str = get_understat_season(season)

        try:
            team_data = client.league('EPL')._get_data(season_str)
        
        except Exception as e:
            logger.error(f'Failed to extract data for {season} season: {e}')
            raise Exception(f'Failed to extract data for {season} season: {e}')
        
        if team_data == []:
            logger.warning(f'No data found for {season} season. Skipping...')
            continue

        # Save the extracted data to a JSON file named with the current date
        file_path = UNDERSTAT_DATA_DIR / 'season_data' / f'season={season}' / f'{CURRENT_DATE}.json'
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(team_data, file, indent=4, ensure_ascii=False)

        logger.info(f'Season data for {season} season saved to {file_path}')

        time.sleep(RATE_LIMIT)


def fetch_match_ids() -> set[str]:
    """Fetches match IDs from latest season data files."""

    logger.info('Extracting match IDs from season data...')

    latest_files = get_latest_season_files()

    match_ids = set()

    for file in latest_files:
        with open(file, 'r', encoding='utf-8') as f:
            season_data = json.load(f)

            season_ids = [match['id'] for match in season_data['dates'] if match['isResult'] == True]

            match_ids.update(season_ids)

    logger.info(f'Extracted {len(match_ids)} unique match IDs from season data.')

    return match_ids


def extract_match_data() -> None:
    """Extracts match data for all matches pulled in season data and saves to JSON file."""

    match_ids = fetch_match_ids()

    logger.info(f'Extracting match data for {len(match_ids)} matches...')

    base_path = UNDERSTAT_DATA_DIR / 'matches'
    base_path.mkdir(parents=True, exist_ok=True)
    
    for match_id in match_ids:
        # Skip file if it already exists
        file_path = base_path / f'match_id={match_id}.json'
        
        if file_path.exists():
            logger.info(f'Match data for match ID {match_id} already exists. Skipping...')
            continue

        fetch_match_data(match_id, base_path)

        time.sleep(RATE_LIMIT)

    logger.info('Completed extraction of match data for all matches.')



def fetch_match_data(match_id: int, base_path: Path) -> None:
    """Fetches match data for a given match ID and saves to JSON file."""

    try:
        match_data = client.match(match_id)._get_data()

        file_path = base_path / f'match_id={match_id}.json'
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(match_data, file, indent=4, ensure_ascii=False)

        logger.info(f'Saved match data for match ID {match_id}')

    except Exception as e:
        logger.error(f'Error fetching match data for match ID {match_id}: {e}')


def extract_id_mappings() -> None:
    """Extracts ID mapping for various player ids and saves as parquet file."""

    url = "https://raw.githubusercontent.com/ChrisMusson/FPL-ID-Map/refs/heads/main/Master.csv"

    logger.info('Extracting ID mappings from GitHub...')

    try:
        df = pd.read_csv(url)

        file_path = UNDERSTAT_DATA_DIR / 'id_mappings' / f'{CURRENT_DATE}.parquet'
        file_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_parquet(file_path, index=False)

        logger.info(f'Saved ID mappings to {file_path}')
    
    except Exception as e:
        logger.error(f'Failed to retrieve ID mappings: {e}')
        raise


extract_season_data()
extract_match_data()
extract_id_mappings()