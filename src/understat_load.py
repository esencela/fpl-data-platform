import psycopg2
from psycopg2.extras import execute_values
import json
import logging
from datetime import datetime
from src.utils.understat_file_helper import (
    get_latest_season_files,
    get_shot_data_files
)

logger = logging.getLogger(__name__)

DB_PARAMS = {
    'dbname': 'fpl_db',
    'user': 'fpl_user',
    'password': 'fpl_password',
    'host': 'localhost',
    'port': 5433
}

def load_season_data_to_postgres() -> None:
    """Loads latest raw season data JSON files into PostgreSQL database."""

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        logger.info('Connected to PostgreSQL database successfully.')
    
    except Exception as e:
        logger.error(f'Failed to connect to PostgreSQL database: {e}')
        return
    
    season_files = get_latest_season_files()

    for file in season_files:
        season = int(file.parent.name.split('=')[1])
        fetch_date = datetime.strptime(file.stem, '%Y-%m-%d')

        with open(file, 'r', encoding='utf-8') as file:
            team_data = json.load(file)

        cursor.execute("""
            INSERT INTO raw.understat_season_data (season, raw_data, fetched_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (season, fetched_at) DO UPDATE
            SET raw_data = EXCLUDED.raw_data, fetched_at = EXCLUDED.fetched_at
        """, (season, json.dumps(team_data), fetch_date))

        conn.commit()
        logger.info(f'Season data for season {season} loaded into PostgreSQL database successfully.')

    cursor.close()
    conn.close()


def load_shot_data_to_postgres() -> None:
    """Loads raw shot data JSON files into PostgreSQL database."""

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        logger.info('Connected to PostgreSQL database successfully.')
    except Exception as e:
        logger.error(f'Failed to connect to PostgreSQL database: {e}')
        return
    
    values = get_shot_data_files()

    query = """
        INSERT INTO raw.understat_shot_data (match_id, raw_data)
        VALUES %s
        ON CONFLICT (match_id) DO UPDATE
        SET raw_data = EXCLUDED.raw_data
    """

    execute_values(cursor, query, values)

    conn.commit()
    cursor.close()
    conn.close()

    logger.info(f'Shot data for {len(values)} matches loaded into PostgreSQL database successfully.')