from sqlalchemy import create_engine
import pandas as pd
import logging
import json
from datetime import datetime
from config.settings import settings
from ingestion.utils.vaastav_file_helper import (
    get_latest_player_files, 
    get_latest_gameweek_files,
    get_latest_fixture_files,
    get_latest_team_files
)

logger = logging.getLogger(__name__)


def get_engine():
    return create_engine(f'postgresql://{settings.postgres_user}:{settings.postgres_password}'
                         f'@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}')


def load_players_to_postgres() -> None:
    """Loads latest raw player parquet files into PostgreSQL database."""

    logger.info('Fetching latest raw player files...')

    player_files = get_latest_player_files()

    for file in player_files:
        season = int(file.parent.name.split('=')[1])
        fetch_date = datetime.strptime(file.stem, '%Y-%m-%d')
        df = pd.read_parquet(file)

        df['season'] = season
        df['fetched_at'] = fetch_date
        df = df.rename(columns={'id': 'player_season_id'})

        # Schema drifts across season, 
        # to handle this keep only essential columns and hold extra columns as JSONB
        known_cols = ['season', 'player_season_id', 'fetched_at']
        extra_cols = [col for col in df.columns if col not in known_cols]

        # Convert extra columns to JSON and store in 'raw_data' column
        df['raw_data'] = df[extra_cols].apply(lambda row: row.to_json(default_handler=str), axis=1)
        df = df[known_cols + ['raw_data']]

        logger.info(f'Loading {file} to PostgreSQL...')

        try:
            df.to_sql('vaastav_players', get_engine(), schema='raw', if_exists='append', index=False)
        except Exception as e:
            logger.error(f'Failed to load player data to database: {e}')
            return

    logger.info(f'Succesfully loaded {len(player_files)} rows to raw.vaastav_players')


def load_gws_to_postgres() -> None:
    """Loads latest raw gws parquet files into PostgreSQL database."""

    logger.info('Fetching latest raw gameweek files...')

    gw_files = get_latest_gameweek_files()

    for file in gw_files:
        season = int(file.parent.name.split('=')[1])
        fetch_date = datetime.strptime(file.stem, '%Y-%m-%d')
        df = pd.read_parquet(file)

        df['season'] = season
        df['fetched_at'] = fetch_date
        df = df.rename(columns={'element': 'player_season_id',
                                 'fixture': 'fixture_season_id',
                                 'round': 'gameweek_id'})

        # Schema drifts across season, 
        # to handle this keep only essential columns and hold extra columns as JSONB
        known_cols = ['season', 'player_season_id', 'fixture_season_id', 'gameweek_id', 'fetched_at']
        extra_cols = [col for col in df.columns if col not in known_cols]

        # Convert extra columns to JSON and store in 'raw_data' column
        df['raw_data'] = df[extra_cols].apply(lambda row: row.to_json(default_handler=str), axis=1)
        df = df[known_cols + ['raw_data']]

        logger.info(f'Loading {file} to PostgreSQL...')

        try:
            df.to_sql('vaastav_gws', get_engine(), schema='raw', if_exists='append', index=False)
        except Exception as e:
            logger.error(f'Failed to load gameweek data to database: {e}')
            return

    logger.info(f'Succesfully loaded {len(gw_files)} rows to raw.vaastav_gws')


def load_fixtures_to_postgres() -> None:
    """Loads latest raw fixture parquet files to PostgreSQL database."""

    logger.info('Fetching latest raw fixture files...')

    fixture_files = get_latest_fixture_files()

    for file in fixture_files:
        season = int(file.parent.name.split('=')[1])
        fetch_date = datetime.strptime(file.stem, '%Y-%m-%d')
        df = pd.read_parquet(file)

        df['season'] = season
        df['fetched_at'] = fetch_date

        df = df.rename(columns={'id': 'fixture_season_id'})

        # Schema drifts across season, 
        # to handle this keep only essential columns and hold extra columns as JSONB
        known_cols = ['season', 'fetched_at', 'fixture_season_id']
        extra_cols = [col for col in df.columns if col not in known_cols]

        # Convert extra columns to JSON and store in 'raw_data' column
        df['raw_data'] = df[extra_cols].apply(lambda row: row.to_json(default_handler=str), axis=1)
        df = df[known_cols + ['raw_data']]

        logger.info(f'Loading {file} to PostgreSQL...')

        try:
            df.to_sql('vaastav_fixtures', get_engine(), schema='raw', if_exists='append', index=False)
        except Exception as e:
            logger.error(f'Failed to load fixture data to database: {e}')
            return

    logger.info(f'Succesfully loaded {len(fixture_files)} rows to raw.vaastav_fixtures')


def load_teams_to_postgres() -> None:
    """Loads latest raw team parquet files to PostgreSQL database."""

    logger.info('Fetching latest raw team files...')

    team_files = get_latest_team_files()

    for file in team_files:
        season = int(file.parent.name.split('=')[1])
        fetch_date = datetime.strptime(file.stem, '%Y-%m-%d')
        df = pd.read_parquet(file)

        df['season'] = season
        df['fetched_at'] = fetch_date

        df = df.rename(columns={'id': 'team_season_id'})

        # Schema drifts across season,
        # to handle this keep only essential columns and hold extra columns as JSONB
        known_cols = ['season', 'team_season_id', 'fetched_at']
        extra_cols = [col for col in df.columns if col not in known_cols]

        # Convert extra columns to JSON and store in 'raw_data' column
        df['raw_data'] = df[extra_cols].apply(lambda row: row.to_json(default_handler=str), axis=1)
        df = df[known_cols + ['raw_data']]

        logger.info(f'Loading {file} to PostgreSQL...')

        try:
            df.to_sql('vaastav_teams', get_engine(), schema='raw', if_exists='append', index=False)
        except Exception as e:
            logger.error(f'Failed to load team data to database: {e}')
            return

    logger.info(f'Succesfully loaded {len(team_files)} rows to raw.vaastav_teams')


def run_vaastav_load() -> None:
    """Runs the full Vaastav loading process for players, gameweeks, fixtures, and teams."""
    
    load_players_to_postgres()
    load_gws_to_postgres()
    load_fixtures_to_postgres()
    load_teams_to_postgres()