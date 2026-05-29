import psycopg2
from psycopg2.extras import execute_values
import json
import logging
from datetime import datetime
from src.ingestion.utils.fpl_file_helper import (
    get_latest_bootstrap_file, 
    get_latest_element_summaries, 
    get_latest_fixtures_file, 
    get_latest_events
)

logger = logging.getLogger(__name__)

# Database connection parameters
DB_PARAMS = {
    'dbname': 'fpl_db',
    'user': 'fpl_user',
    'password': 'fpl_password',
    'host': 'localhost',
    'port': 5433
}

def load_bootstrap_to_postgres():
    """Loads latest raw bootstrap JSON data into PostgreSQL database."""    

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        logger.info('Connected to PostgreSQL database successfully.')
    except Exception as e:
        logger.error(f'Failed to connect to PostgreSQL database: {e}')
        return
    
    # Load latest bootstrap JSON file into postgres
    bootstrap_file = get_latest_bootstrap_file()

    with open(bootstrap_file, 'r', encoding='utf-8') as file:
        bootstrap_data = json.load(file)

    season = int(bootstrap_file.parent.name.split('=')[1])
    fetch_date = datetime.strptime(bootstrap_file.stem, '%Y-%m-%d')

    cursor.execute("""
        INSERT INTO raw.fpl_bootstrap_static (season, raw_data, fetched_at) 
        VALUES (%s, %s, %s)
        ON CONFLICT (season, fetched_at) DO UPDATE
        SET raw_data = EXCLUDED.raw_data, fetched_at = EXCLUDED.fetched_at
    """, (season, json.dumps(bootstrap_data), fetch_date))

    conn.commit()
    cursor.close()
    conn.close()
    logger.info('Bootstrap data loaded into PostgreSQL database successfully.')


def load_element_summaries_to_postgres():
    """Loads latest raw element summary JSON data into PostgreSQL database."""
    
    values = get_latest_element_summaries()

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        logger.info('Connected to PostgreSQL database successfully.')
    except Exception as e:
        logger.error(f'Failed to connect to PostgreSQL database: {e}')
        return
    
    query = """
        INSERT INTO raw.fpl_element_summary (season, player_id, raw_data, fetched_at) 
        VALUES %s
        ON CONFLICT (season, player_id) DO UPDATE 
        SET raw_data = EXCLUDED.raw_data, fetched_at = EXCLUDED.fetched_at
    """

    execute_values(cursor, query, values)

    conn.commit()
    cursor.close()
    conn.close()
    logger.info('Element summary data loaded into PostgreSQL database successfully.')
        

def load_fixtures_to_postgres():
    """Loads latest raw fixtures JSON data into PostgreSQL database."""
    
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        logger.info('Connected to PostgreSQL database successfully.')
    except Exception as e:
        logger.error(f'Failed to connect to PostgreSQL database: {e}')
        return
    
    # Load latest fixtures JSON file into postgres
    fixtures_file = get_latest_fixtures_file()

    with open(fixtures_file, 'r', encoding='utf-8') as file:
        fixtures_data = json.load(file)

    season = int(fixtures_file.parent.name.split('=')[1])
    fetch_date = datetime.strptime(fixtures_file.stem, '%Y-%m-%d')

    cursor.execute("""
        INSERT INTO raw.fpl_fixtures (season, raw_data, fetched_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (season, fetched_at) DO UPDATE
        SET raw_data = EXCLUDED.raw_data, fetched_at = EXCLUDED.fetched_at
    """, (season, json.dumps(fixtures_data), fetch_date))

    conn.commit()
    cursor.close()
    conn.close()
    logger.info('Fixture data loaded into PostgreSQL database successfully.')


def load_events_to_postgres():
    """Loads latest raw events JSON data into PostgreSQL database."""
    
    values = get_latest_events()

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        logger.info('Connected to PostgreSQL database successfully.')
    except Exception as e:
        logger.error(f'Failed to connect to PostgreSQL database: {e}')
        return
    
    query = """
        INSERT INTO raw.fpl_events (season, gameweek_id, raw_data, fetched_at) 
        VALUES %s
        ON CONFLICT (season, gameweek_id) DO UPDATE
        SET raw_data = EXCLUDED.raw_data, fetched_at = EXCLUDED.fetched_at
    """

    execute_values(cursor, query, values)

    conn.commit()
    cursor.close()
    conn.close()
    logger.info('Event data loaded into PostgreSQL database successfully.')