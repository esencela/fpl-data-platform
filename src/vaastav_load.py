from sqlalchemy import create_engine
import pandas as pd
import logging
import json
from datetime import datetime
from src.utils.vaastav_file_helper import get_latest_player_files

logger = logging.getLogger(__name__)

engine = create_engine('postgresql://fpl_user:fpl_password@localhost:5433/fpl_db')


def load_players_to_postgres() -> None:
    """Loads latest raw player parquet file into postgreSQL database."""

    player_files = get_latest_player_files()

    for file in player_files:
        season = int(file.parent.name.split('=')[1])
        fetch_date = datetime.strptime(file.stem, '%Y-%m-%d')
        df = pd.read_parquet(file)

        df['season'] = season
        df['fetched_at'] = fetch_date
        df = df.rename(columns={'id': 'player_season_id'})

        # Hold columns in a 'raw_data' JSONB column, only keeping season, player_season_id, and fetched_at
        known_cols = ['season', 'player_season_id', 'fetched_at']
        extra_cols = [col for col in df.columns if col not in known_cols]

        # Convert extra columns to JSON and store in 'raw_data' column
        df['raw_data'] = df[extra_cols].apply(lambda row: row.to_json(default_handler=str), axis=1)
        df = df[known_cols + ['raw_data']]

        df.to_sql('vaastav_players', engine, schema='raw', if_exists='append', index=False)