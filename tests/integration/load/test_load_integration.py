import pytest
import json
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
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


@pytest.fixture
def get_test_engine(test_db_params):
    return create_engine(f'postgresql://{test_db_params["user"]}:{test_db_params["password"]}'
                         f'@{test_db_params["host"]}:{test_db_params["port"]}/{test_db_params["dbname"]}')


@pytest.fixture()
def vaastav_players(tmp_path):
    # Create mock player parquet file
    season_dir = tmp_path / 'season=2026'
    season_dir.mkdir()

    player_file = season_dir / '2026-05-01.parquet'

    df_player = pd.DataFrame({
        'id': [1, 2, 3],
        'web_name': ['Salah', 'Haaland', 'Mainoo'],
        'goals': [0, 0, 3]
    })

    df_player.to_parquet(player_file, index=False)

    return [player_file]


def test_vaastav_load_players_to_postgres(monkeypatch, test_db_params, get_test_engine, vaastav_players):
    # Patch necessary functions
    monkeypatch.setattr(
        'ingestion.load.vaastav_load.get_engine',
        lambda: get_test_engine
    )
    monkeypatch.setattr(
        'ingestion.load.vaastav_load.get_latest_player_files',
        lambda: vaastav_players
    )

    vaastav_load.load_players_to_postgres()

    conn = psycopg2.connect(**test_db_params)

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT season, player_season_id, fetched_at, raw_data
            FROM raw.vaastav_players
        """)

        rows = cursor.fetchall()

    conn.close()

    # Assert correct data has been loaded to database
    assert len(rows) == 3

    season, player_id, fetched_at, raw_data = rows[0]

    assert season == 2026
    assert player_id == 1
    assert fetched_at.strftime('%Y-%m-%d') == '2026-05-01'

    assert raw_data == {
        'web_name': 'Salah',
        'goals': 0
    }


@pytest.fixture
def vaastav_gws(tmp_path):
    # Create mock gameweek parquet file
    season_dir = tmp_path / 'season=2026'
    season_dir.mkdir()
    gw_file = season_dir / '2026-05-01.parquet'

    df_gw = pd.DataFrame({
        'element': [0, 1],
        'fixture': [1, 1],
        'round': [31, 32],
        'web_name': ['player1', 'player2'],
        'minutes': [90, 67]
    })

    df_gw.to_parquet(gw_file, index=False)

    return [gw_file]


def test_vaastav_load_gws_to_postgres(monkeypatch, test_db_params, get_test_engine, vaastav_gws):
    # Patch necessary functions
    monkeypatch.setattr(
        'ingestion.load.vaastav_load.get_engine',
        lambda: get_test_engine
    )
    monkeypatch.setattr(
        'ingestion.load.vaastav_load.get_latest_gameweek_files',
        lambda: vaastav_gws
    )

    vaastav_load.load_gws_to_postgres()

    conn = psycopg2.connect(**test_db_params)

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT season, player_season_id, fixture_season_id, gameweek_id, fetched_at, raw_data
            FROM raw.vaastav_gws
        """)

        rows = cursor.fetchall()

    conn.close()

    # Assert correct data has been loaded to database
    assert len(rows) == 2

    season, player_id, fixture_id, gw_id, fetched_at, raw_data = rows[0]

    assert season == 2026
    assert player_id == 0
    assert fixture_id == 1
    assert gw_id == 31
    assert fetched_at.strftime('%Y-%m-%d') == '2026-05-01'

    assert raw_data == {
        'web_name': 'player1',
        'minutes': 90
    }


@pytest.fixture
def vaastav_fixtures(tmp_path):
    # Create mock gameweek parquet file
    season_dir = tmp_path / 'season=2026'
    season_dir.mkdir()
    file = season_dir / '2026-05-01.parquet'

    df_fixture = pd.DataFrame({
        'id': [0, 1],
        'code': [111000, 232939],
        'team_h': [3, 5]
    })

    df_fixture.to_parquet(file, index=False)

    return [file]


def test_vaastav_load_fixtures_to_postgres(monkeypatch, test_db_params, get_test_engine, vaastav_fixtures):
    # Patch necessary functions
    monkeypatch.setattr(
        'ingestion.load.vaastav_load.get_engine',
        lambda: get_test_engine
    )
    monkeypatch.setattr(
        'ingestion.load.vaastav_load.get_latest_fixture_files',
        lambda: vaastav_fixtures
    )

    vaastav_load.load_fixtures_to_postgres()

    conn = psycopg2.connect(**test_db_params)

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT season, fixture_season_id, fetched_at, raw_data
            FROM raw.vaastav_fixtures
        """)

        rows = cursor.fetchall()

    conn.close()

    # Assert correct data has been loaded to database
    assert len(rows) == 2

    season, fixture_id, fetched_at, raw_data = rows[0]

    assert season == 2026
    assert fixture_id == 0
    assert fetched_at.strftime('%Y-%m-%d') == '2026-05-01'

    assert raw_data == {
        'code': 111000,
        'team_h': 3
    }


@pytest.fixture
def vaastav_teams(tmp_path):
    # Create mock gameweek parquet file
    season_dir = tmp_path / 'season=2026'
    season_dir.mkdir()
    file = season_dir / '2026-05-01.parquet'

    df_team = pd.DataFrame({
        'id': [0, 1],
        'code': [4, 17],
        'name': ['Team A', 'Team B']
    })

    df_team.to_parquet(file, index=False)

    return [file]


def test_vaastav_load_fixtures_to_postgres(monkeypatch, test_db_params, get_test_engine, vaastav_teams):
    # Patch necessary functions
    monkeypatch.setattr(
        'ingestion.load.vaastav_load.get_engine',
        lambda: get_test_engine
    )
    monkeypatch.setattr(
        'ingestion.load.vaastav_load.get_latest_team_files',
        lambda: vaastav_teams
    )

    vaastav_load.load_teams_to_postgres()

    conn = psycopg2.connect(**test_db_params)

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT season, team_season_id, fetched_at, raw_data
            FROM raw.vaastav_teams
        """)

        rows = cursor.fetchall()

    conn.close()

    # Assert correct data has been loaded to database
    assert len(rows) == 2

    season, team_id, fetched_at, raw_data = rows[0]

    assert season == 2026
    assert team_id == 0
    assert fetched_at.strftime('%Y-%m-%d') == '2026-05-01'

    assert raw_data == {
        'code': 4,
        'name': 'Team A'
    }


@pytest.fixture
def understat_season_data(tmp_path):
    # Create mock season json file
    season_dir = tmp_path / 'season=2026'
    season_dir.mkdir()
    season_file = season_dir / '2026-05-01.json'
    season_data = {'teams': {'id': 1, 'title': 'Team'}, 'players': [{'id': 2, 'name': 'Player'}]}
    season_file.write_text(json.dumps(season_data))

    return [season_file]


def test_understat_load_season_data_to_postgres(understat_season_data, monkeypatch, test_db_params):
    # Patch get file function
    monkeypatch.setattr(
        'ingestion.load.understat_load.get_latest_season_files',
        lambda: understat_season_data
    )

    understat_load.load_season_data_to_postgres(db_params=test_db_params)

    conn = psycopg2.connect(**test_db_params)

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT season, raw_data, fetched_at
            FROM raw.understat_season_data
        """)

        rows = cursor.fetchall()

    conn.close()

    # Assert correct data has been loaded to database
    season, raw_data, fetched_at = rows[0]

    assert season == 2026
    assert fetched_at.strftime('%Y-%m-%d') == '2026-05-01'

    assert raw_data == {
        'teams': {'id': 1, 'title': 'Team'}, 'players': [{'id': 2, 'name': 'Player'}]
    }


@pytest.fixture
def understat_match_data():
    # Create mock match data
    match_data = [
        (1, json.dumps({'roster': {'h': {'1': {'id': 1, 'goals': 2}}}})),
        (2, json.dumps({'roster': {'a': {'2': {'id': 3, 'goals': 4}}}}))
    ]

    return match_data


def test_understat_load_match_data_to_postgres(understat_match_data, monkeypatch, test_db_params):
    # Patch get files function
    monkeypatch.setattr(
        'ingestion.load.understat_load.get_latest_match_files',
        lambda: understat_match_data
    )

    understat_load.load_match_data_to_postgres(db_params=test_db_params)

    conn = psycopg2.connect(**test_db_params)

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT match_id, raw_data
            FROM raw.understat_match_data
        """)

        rows = cursor.fetchall()

    conn.close()

    # Assert correct data has been loaded to database
    assert len(rows) == 2

    match_id, raw_data = rows[0]

    assert match_id == 1
    assert raw_data == {
        'roster': {'h': {'1': {'id': 1, 'goals': 2}}}
    }


@pytest.fixture
def id_mappings(tmp_path):
    # Create mock id mappings parquet file
    file = tmp_path / '2026-05-01.parquet'

    mock_df = pd.DataFrame({
        'code': [1, 2, 3],
        'fbref': [1, 2, 3],
        'understat': [6, 7, 8]
    })

    mock_df.to_parquet(file, index=False)

    return file


def test_understat_load_id_mappings_to_postgres(id_mappings, monkeypatch, get_test_engine, test_db_params):
    # Patch necessary functions
    monkeypatch.setattr(
        'ingestion.load.understat_load.get_latest_id_mappings_file',
        lambda: id_mappings
    )
    monkeypatch.setattr(
        'ingestion.load.understat_load.get_engine',
        lambda: get_test_engine
    )

    understat_load.load_id_mappings_to_postgres()

    conn = psycopg2.connect(**test_db_params)

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT code, raw_data, fetched_at
            FROM raw.id_mappings
        """)

        rows = cursor.fetchall()

    conn.close()

    # Assert correct data has been loaded to database
    assert len(rows) == 3

    code, raw_data, fetched_at = rows[0]

    assert code == 1
    assert fetched_at.strftime('%Y-%m-%d') == '2026-05-01'

    assert raw_data == {
        'fbref': 1,
        'understat': 6
    }