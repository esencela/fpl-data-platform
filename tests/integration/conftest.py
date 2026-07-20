import os
from pathlib import Path
import pytest
import psycopg2
from testcontainers.postgres import PostgresContainer

SQL_INIT_DIR = Path(__file__).resolve().parents[2] / 'sql' / 'init'
RAW_TABLES = [
    'raw.fpl_bootstrap_static', 
    'raw.fpl_element_summary',
    'raw.fpl_fixtures',
    'raw.fpl_events',
    'raw.vaastav_players',
    'raw.vaastav_gws',
    'raw.vaastav_fixtures',
    'raw.vaastav_teams',
    'raw.understat_season_data',
    'raw.understat_match_data',
    'raw.id_mappings'
]


@pytest.fixture(scope='session')
def postgres_container():
    """Starts a PostgreSQL container with correct schema and tables."""

    with PostgresContainer('postgres:15').with_volume_mapping(
        str(SQL_INIT_DIR), '/docker-entrypoint-initdb.d'
    ) as container:
        yield container

    
@pytest.fixture(scope='session', autouse=True)
def db_params(postgres_container):
    """Returns a dict of postgres container connection details."""

    return {
        'dbname': postgres_container.dbname,
        'user': postgres_container.username,
        'password': postgres_container.password,
        'host': postgres_container.get_container_host_ip(),
        'port': postgres_container.get_exposed_port(5432)
    }


@pytest.fixture
def clean_db(db_params):
    """Truncates all tables and indices from postgres container before every test."""
    conn = psycopg2.connect(**db_params)
    
    with conn.cursor() as cursor:
        cursor.execute(f'TRUNCATE {", ".join(RAW_TABLES)} RESTART IDENTITY;')

    conn.commit()
    conn.close()
    yield