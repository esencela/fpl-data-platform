from pathlib import Path
import pytest
import psycopg2
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope='session')
def features_db():
    """Starts a PostgreSQL container with custom schema and tables."""

    # Create features table to test prediction features loading
    with PostgresContainer('postgres:15') as container:
        db_url = container.get_connection_url()
        engine = create_engine(db_url)

        with engine.begin() as conn:
            # Create schema and table for prediction features
            conn.execute(text('CREATE SCHEMA IF NOT EXISTS test_schema'))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_schema.test_features (
                    fixture_key TEXT,
                    player_id INTEGER,
                    feature_1 TEXT,
                    feature_2 FLOAT
                );
            """))

            # Insert sample data into the features table
            df_features = pd.DataFrame({
                'fixture_key': ['fixture_1', 'fixture_2'],
                'player_id': [1, 2],
                'feature_1': ['A', 'B'],
                'feature_2': [0.5, np.nan]
            })

            df_features.to_sql('test_features', conn, schema='test_schema', if_exists='append', index=False)

        engine.dispose()
        yield db_url
        