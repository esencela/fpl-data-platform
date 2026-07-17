import psycopg2
from psycopg2.extras import execute_values
from sqlalchemy import create_engine
import pandas as pd
import json
import logging
from datetime import datetime
from config.settings import settings
from ingestion.utils.understat_file_helper import (
    get_latest_season_files,
    get_latest_match_files,
    get_latest_id_mappings_file
)

logger = logging.getLogger(__name__)

# Database connection parameters
DB_PARAMS = {
    'dbname': settings.postgres_db,
    'user': settings.postgres_user,
    'password': settings.postgres_password,
    'host': settings.postgres_host,
    'port': settings.postgres_port
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


def load_match_data_to_postgres() -> None:
    """Loads raw match data JSON files into PostgreSQL database."""

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        logger.info('Connected to PostgreSQL database successfully.')
    except Exception as e:
        logger.error(f'Failed to connect to PostgreSQL database: {e}')
        return
    
    values = get_latest_match_files()

    query = """
        INSERT INTO raw.understat_match_data (match_id, raw_data)
        VALUES %s
        ON CONFLICT (match_id) DO UPDATE
        SET raw_data = EXCLUDED.raw_data
    """

    execute_values(cursor, query, values)

    conn.commit()
    cursor.close()
    conn.close()

    logger.info(f'Match data for {len(values)} matches loaded into PostgreSQL database successfully.')


def load_id_mappings_to_postgres() -> None:
    """Loads player and team ID mapping data into PostgreSQL database."""

    file = get_latest_id_mappings_file()

    df = pd.read_parquet(file)
    fetch_date = datetime.strptime(file.stem, '%Y-%m-%d')
    df['fetched_at'] = fetch_date

    # Store extra columns as JSONB to handle upstream schema changes without breaking the load process
    known_cols = ['code', 'fetched_at']
    extra_cols = [col for col in df.columns if col not in known_cols]

    df['raw_data'] = df[extra_cols].apply(lambda row: row.to_json(default_handler=str), axis=1)
    df = df[known_cols + ['raw_data']]

    engine = create_engine(f'postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}')

    try:
        df.to_sql('id_mappings', engine, schema='raw', if_exists='append', index=False)
    except Exception as e:
        logger.error(f'Failed to load id mappings to database: {e}')
        return

    logger.info(f'ID mappings data loaded into PostgreSQL database successfully.')


def run_understat_load() -> None:
    """Runs the full Understat loading process for season data, match data, and ID mappings."""

    load_season_data_to_postgres()
    load_match_data_to_postgres()
    load_id_mappings_to_postgres()