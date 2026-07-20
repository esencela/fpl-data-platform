import pytest
import json
import psycopg2
from ingestion.load import fpl_load, vaastav_load, understat_load


@pytest.fixture
def bootstrap_file(tmp_path):
    # Create mock bootstrap json file
    season_dir = tmp_path / 'season=2026'
    season_dir.mkdir()

    file = season_dir / '2026-05-01.json'

    data = {
        'elements': [{'id': 1, 'name': 'Gameweek 1'}, {'id': 2, 'name': 'Gameweek 2'}],
        'events': [{'id': 3, 'web_name': 'Player 3'}, {'id': 4, 'web_name': 'Player 4'}]
    }

    file.write_text(json.dumps(data))

    return file


def test_fpl_load_bootstrap_to_postgres(bootstrap_file, monkeypatch, test_db_params):
    # Patch mock bootstrap file
    monkeypatch.setattr(
        'ingestion.load.fpl_load.get_latest_bootstrap_file', 
        lambda: bootstrap_file
    )
    
    fpl_load.load_bootstrap_to_postgres(db_params=test_db_params)

    conn = psycopg2.connect(**test_db_params)

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT season, raw_data, fetched_at
            FROM raw.fpl_bootstrap_static
        """)

        rows = cursor.fetchall()

    conn.close()

    # Assert correct data has been loaded to database
    assert len(rows) == 1

    season, raw_data, fetched_at = rows[0]

    assert season == 2026
    assert fetched_at.strftime('%Y-%m-%d') == '2026-05-01'

    assert raw_data == {
        'elements': [{'id': 1, 'name': 'Gameweek 1'}, {'id': 2, 'name': 'Gameweek 2'}],
        'events': [{'id': 3, 'web_name': 'Player 3'}, {'id': 4, 'web_name': 'Player 4'}]
    }


@pytest.fixture
def fpl_element_summaries():
    # Create mock element summary response
    element_summaries = [
        (2026, 1, json.dumps({'fixtures': '', 'history': ''}), '2026-05-01'),
        (2026, 2, json.dumps({'fixtures': '', 'history': ''}), '2026-05-01'),
        (2026, 3, json.dumps({'fixtures': '', 'history': ''}), '2026-05-01')
    ]

    return element_summaries


def test_fpl_load_element_summaries_to_postgres(fpl_element_summaries, monkeypatch, test_db_params):
    # Patch mock element summaries
    monkeypatch.setattr(
        'ingestion.load.fpl_load.get_latest_element_summaries',
        lambda: fpl_element_summaries
    )

    fpl_load.load_element_summaries_to_postgres(db_params=test_db_params)

    conn = psycopg2.connect(**test_db_params)

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT season, player_id, raw_data, fetched_at
            FROM raw.fpl_element_summary
        """)

        rows = cursor.fetchall()

    conn.close()

    # Assert correct data has been loaded to database
    assert len(rows) == 3

    season, player_id, raw_data, fetched_at = rows[1]

    assert season == 2026
    assert player_id == 2
    assert fetched_at.strftime('%Y-%m-%d') == '2026-05-01'

    assert raw_data == {'fixtures': '', 'history': ''}


def test_fpl_load_fixtures_to_postgres(bootstrap_file, monkeypatch, test_db_params):
    # Reuse bootstrap file as it has the same structure
    monkeypatch.setattr(
        'ingestion.load.fpl_load.get_latest_fixtures_file', 
        lambda: bootstrap_file
    )
    
    fpl_load.load_fixtures_to_postgres(db_params=test_db_params)

    conn = psycopg2.connect(**test_db_params)

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT season, raw_data, fetched_at
            FROM raw.fpl_fixtures
        """)

        rows = cursor.fetchall()

    conn.close()

    # Assert correct data has been loaded to database
    assert len(rows) == 1

    season, raw_data, fetched_at = rows[0]

    assert season == 2026
    assert fetched_at.strftime('%Y-%m-%d') == '2026-05-01'

    assert raw_data == {
        'elements': [{'id': 1, 'name': 'Gameweek 1'}, {'id': 2, 'name': 'Gameweek 2'}],
        'events': [{'id': 3, 'web_name': 'Player 3'}, {'id': 4, 'web_name': 'Player 4'}]
    }


def test_fpl_load_events_to_postgres(fpl_element_summaries, monkeypatch, test_db_params):
    # Reuse element summaries as it has the same structure
    monkeypatch.setattr(
        'ingestion.load.fpl_load.get_latest_events',
        lambda: fpl_element_summaries
    )

    fpl_load.load_events_to_postgres(db_params=test_db_params)

    conn = psycopg2.connect(**test_db_params)

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT season, gameweek_id, raw_data, fetched_at
            FROM raw.fpl_events
        """)

        rows = cursor.fetchall()

    conn.close()

    # Assert correct data has been loaded to database
    assert len(rows) == 3

    season, gameweek_id, raw_data, fetched_at = rows[1]

    assert season == 2026
    assert gameweek_id == 2
    assert fetched_at.strftime('%Y-%m-%d') == '2026-05-01'

    assert raw_data == {'fixtures': '', 'history': ''}