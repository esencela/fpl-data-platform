import os
from pathlib import Path
import pytest
import psycopg2
from testcontainers.postgres import PostgresContainer

os.environ.setdefault('RAW_DATA_DIR', '/tmp/test_data')

os.environ.setdefault('POSTGRES_DB', 'fpl_test')
os.environ.setdefault('POSTGRES_USER', 'test_user')
os.environ.setdefault('POSTGRES_PASSWORD', 'test_password')
os.environ.setdefault('POSTGRES_HOST', 'localhost')

SQL_INIT_DIR = Path(__file__).parent.parent / 'sql' / 'init'
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

    
@pytest.fixture(scope='session')
def db_params(postgres_container):
    """Returns a dict of postgres container connection details."""

    return {
        'dbname': postgres_container.dbname,
        'username': postgres_container.username,
        'password': postgres_container.password,
        'host': postgres_container.get_container_host_ip,
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


@pytest.fixture
def loader_db_params(db_params, clean_db, monkeypatch):
    """Set loading scripts DB_PARAMS to connect to test container"""

    monkeypatch.setattr('ingestion.load.fpl_load.DB_PARAMS', db_params)
    return db_params