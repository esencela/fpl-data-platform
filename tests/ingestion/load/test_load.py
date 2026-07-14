import json
import pandas as pd
from unittest.mock import patch, MagicMock
import pytest
import logging
from ingestion.load import fpl_load, vaastav_load, understat_load


def test_fpl_load_bootstrap_to_postgres_success(tmp_path):
    # Create file on tmp path in expected file structure
    season_dir = tmp_path / 'season=2026' 
    season_dir.mkdir(parents=True, exist_ok=True)
    bootstrap_file = season_dir / '2026-05-01.json'
    bootstrap_data = {'elements': [], 'teams': [], 'events': []}
    bootstrap_file.write_text(json.dumps(bootstrap_data))

    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch('ingestion.load.fpl_load.get_latest_bootstrap_file', return_value=bootstrap_file), \
         patch('ingestion.load.fpl_load.psycopg2.connect', return_value=mock_conn):
        
        fpl_load.load_bootstrap_to_postgres()

    # Assert cursor execute was called
    mock_cursor.execute.assert_called_once()

    args = mock_cursor.execute.call_args[0]
    sql, params = args
    season, raw_data, fetched_at = params

    # Assert correct values were passed
    assert season == 2026
    assert json.loads(raw_data) == bootstrap_data
    assert fetched_at.strftime('%Y-%m-%d') == '2026-05-01'

    # Assert commit and close were called
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


def test_fpl_load_bootstrap_to_postgres_failure():
    with patch('ingestion.load.fpl_load.get_latest_bootstrap_file') as mock_get, \
         patch('ingestion.load.fpl_load.psycopg2.connect') as mock_conn:        
        
        mock_conn.side_effect = Exception()
        fpl_load.load_bootstrap_to_postgres()

    # Assert bootstrap file is not fetched on connection failure
    mock_conn.assert_called_once()
    mock_get.assert_not_called()


def test_fpl_load_element_summaries_to_postgres_success():
    # Create mock list of records
    element_summaries = [
        (2026, 1, {'fixtures': '', 'history': ''}, '2026-05-01'),
        (2026, 2, {'fixtures': '', 'history': ''}, '2026-05-01'),
        (2026, 3, {'fixtures': '', 'history': ''}, '2026-05-01')
    ]

    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch('ingestion.load.fpl_load.get_latest_element_summaries', return_value=element_summaries), \
         patch('ingestion.load.fpl_load.psycopg2.connect', return_value=mock_conn), \
         patch('ingestion.load.fpl_load.execute_values') as mock_execute:
        
        fpl_load.load_element_summaries_to_postgres()

    # Assert execute values was called with correct records
    mock_execute.assert_called_once()
    args = mock_execute.call_args[0]
    values = args[2]
    assert values == element_summaries

    # Assert commit and close were called
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


def test_fpl_load_element_summaries_to_postgres_failure():
    with patch('ingestion.load.fpl_load.psycopg2.connect') as mock_conn, \
         patch('ingestion.load.fpl_load.execute_values') as mock_execute:        
        
        mock_conn.side_effect = Exception()
        fpl_load.load_element_summaries_to_postgres()

    # Assert execute values is not called on connection failure
    mock_conn.assert_called_once()
    mock_execute.assert_not_called()


def test_fpl_load_fixtures_to_postgres_success(tmp_path):
    season_dir = tmp_path / "season=2026"
    season_dir.mkdir(parents=True, exist_ok=True)
    fixtures_file = season_dir / '2026-05-01.json'
    fixtures_data = {'code': 1, 'team_h': 1, 'team_a': 2}
    fixtures_file.write_text(json.dumps(fixtures_data))

    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch('ingestion.load.fpl_load.get_latest_fixtures_file', return_value=fixtures_file), \
         patch('ingestion.load.fpl_load.psycopg2.connect', return_value=mock_conn):
        
        fpl_load.load_fixtures_to_postgres()

    # Assert execute was called once wirh correct params
    mock_cursor.execute.assert_called_once()

    args = mock_cursor.execute.call_args[0]
    sql, params = args
    season, data, fetch_date = params

    assert season == 2026
    assert json.loads(data) == fixtures_data
    assert fetch_date.strftime('%Y-%m-%d') == '2026-05-01' 

    # Assert commit and close were called
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


def test_fpl_load_fixtures_to_postgres_failure():
    with patch('ingestion.load.fpl_load.get_latest_fixtures_file') as mock_get, \
         patch('ingestion.load.fpl_load.psycopg2.connect') as mock_conn:
        
        mock_conn.side_effect = Exception('Failed to connect to PostgreSQL database')
        fpl_load.load_fixtures_to_postgres()

    # Assert fixtures file is not fetched on connection failure
    mock_conn.assert_called_once()
    mock_get.assert_not_called()


def test_load_events_to_postgres_success():
    # Create mock list of records
    events = [
        ({'elements': [{'id': 1}]}),
        ({'elements': [{'id': 2}]}),
        ({'elements': [{'id': 3}]}),
    ]

    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch('ingestion.load.fpl_load.get_latest_events', return_value=events), \
         patch('ingestion.load.fpl_load.psycopg2.connect', return_value=mock_conn), \
         patch('ingestion.load.fpl_load.execute_values') as mock_execute:
        
        fpl_load.load_events_to_postgres()

    # Assert execute values was called with correct records
    mock_execute.assert_called_once()
    args = mock_execute.call_args[0]
    values = args[2]
    assert values == events

    # Assert commit and close were called
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


def test_fpl_load_element_summaries_to_postgres_failure():
    with patch('ingestion.load.fpl_load.psycopg2.connect') as mock_conn, \
         patch('ingestion.load.fpl_load.execute_values') as mock_execute:        
        
        mock_conn.side_effect = Exception()
        fpl_load.load_events_to_postgres()

    # Assert execute values is not called on connection failure
    mock_conn.assert_called_once()
    mock_execute.assert_not_called()


def test_vaastav_load_players_to_postgres_success():
    # Create mock file with correct hierarchy
    mock_file = MagicMock()
    mock_file.parent.name = 'season=2026'
    mock_file.stem = '2026-05-01'

    # Create mock player dataframe
    mock_df = pd.DataFrame({
        'id': [1, 2, 3],
        'web_name': ['Salah', 'Haaland', 'Mainoo'],
        'goals': [0, 0, 3]
    })

    with patch('ingestion.load.vaastav_load.get_latest_player_files', return_value=[mock_file]), \
         patch('ingestion.load.vaastav_load.pd.read_parquet', return_value=mock_df), \
         patch('ingestion.load.vaastav_load.get_engine'), \
         patch('pandas.DataFrame.to_sql', autospec=True) as mock_sql:
        
        vaastav_load.load_players_to_postgres()

    mock_sql.assert_called_once()

    # Assert to_sql was called with correct params
    params = mock_sql.call_args
    df = params.args[0]
    table_name = params.args[1]
    kwargs = params.kwargs

    assert table_name == 'vaastav_players'
    assert kwargs == {'schema': 'raw', 'if_exists': 'append', 'index': False}

    # Assert correct passed dataframe values
    assert list(df.columns) == ['season', 'player_season_id', 'fetched_at', 'raw_data']
    assert (df['season'] == 2026).all()
    assert (df['fetched_at'].dt.strftime('%Y-%m-%d') == '2026-05-01').all()

    assert list(df['player_season_id']) == [1, 2, 3]

    first_row_raw_data = json.loads(df['raw_data'].iloc[0])
    assert first_row_raw_data == {'web_name': 'Salah', 'goals': 0}


def test_vaastav_load_players_to_postgres_failure(caplog):
    # Create mock file with correct hierarchy
    mock_file = MagicMock()
    mock_file.parent.name = 'season=2026'
    mock_file.stem = '2026-05-01'

    # Create mock player dataframe
    mock_df = pd.DataFrame({
        'id': [1, 2, 3],
        'web_name': ['Salah', 'Haaland', 'Mainoo'],
        'goals': [0, 0, 3]
    })

    with patch('ingestion.load.vaastav_load.get_latest_player_files', return_value=[mock_file]), \
         patch('ingestion.load.vaastav_load.pd.read_parquet', return_value=mock_df), \
         patch('ingestion.load.vaastav_load.get_engine'), \
         patch('pandas.DataFrame.to_sql', autospec=True) as mock_sql, \
         caplog.at_level(logging.ERROR):
        
        mock_sql.side_effect = Exception('Failed to connect')
        vaastav_load.load_players_to_postgres()

    mock_sql.assert_called_once()
    assert 'Failed to connect' in caplog.text


def test_vaastav_load_gws_to_postgres_success():
    # Create mock file with correct hierarchy
    mock_file = MagicMock()
    mock_file.parent.name = 'season=2026'
    mock_file.stem = '2026-05-01'

    # Create mock gameweek dataframe
    mock_df = pd.DataFrame({
        'element': [0, 1],
        'fixture': [1, 1],
        'round': [31, 32],
        'web_name': ['player1', 'player2'],
        'minutes': [90, 67]
    })

    with patch('ingestion.load.vaastav_load.get_latest_gameweek_files', return_value=[mock_file]), \
         patch('ingestion.load.vaastav_load.pd.read_parquet', return_value=mock_df), \
         patch('ingestion.load.vaastav_load.get_engine'), \
         patch('pandas.DataFrame.to_sql', autospec=True) as mock_sql:
        
        vaastav_load.load_gws_to_postgres()

    mock_sql.assert_called_once()

    # Assert to_sql was called with the correct params
    params = mock_sql.call_args
    df = params.args[0]
    table_name = params.args[1]
    kwargs = params.kwargs

    assert table_name == 'vaastav_gws'
    assert kwargs == {'schema': 'raw', 'if_exists': 'append', 'index': False}

    # Assert correct passed DataFrame values
    assert list(df.columns) == ['season', 'player_season_id', 'fixture_season_id', 'gameweek_id', 'fetched_at', 'raw_data']
    assert (df['season'] == 2026).all()
    assert (df['fetched_at'].dt.strftime('%Y-%m-%d') == '2026-05-01').all()

    assert list(df['player_season_id']) == [0, 1]
    assert list(df['fixture_season_id']) == [1, 1]
    assert list(df['gameweek_id']) == [31, 32]

    first_row_raw_data = json.loads(df['raw_data'].iloc[0])
    assert first_row_raw_data == {'web_name': 'player1', 'minutes': 90}


def test_vaastav_load_gws_to_postgres_failure(caplog):
    # Create mock file with correct hierarchy
    mock_file = MagicMock()
    mock_file.parent.name = 'season=2026'
    mock_file.stem = '2026-05-01'

    # Create mock gameweek dataframe
    mock_df = pd.DataFrame({
        'element': [0, 1],
        'fixture': [1, 1],
        'round': [31, 32],
        'web_name': ['player1', 'player2'],
        'minutes': [90, 67]
    })

    with patch('ingestion.load.vaastav_load.get_latest_gameweek_files', return_value=[mock_file]), \
         patch('ingestion.load.vaastav_load.pd.read_parquet', return_value=mock_df), \
         patch('ingestion.load.vaastav_load.get_engine'), \
         patch('pandas.DataFrame.to_sql', autospec=True) as mock_sql, \
         caplog.at_level(logging.ERROR):
        
        mock_sql.side_effect = Exception('Failed to connect')
        vaastav_load.load_gws_to_postgres()

    mock_sql.assert_called_once()
    assert 'Failed to connect' in caplog.text


def test_vaastav_load_fixtures_to_postgres_success():
    # Create mock file with correct hierarchy
    mock_file = MagicMock()
    mock_file.parent.name = 'season=2026'
    mock_file.stem = '2026-05-01'

    # Create mock gameweek dataframe
    mock_df = pd.DataFrame({
        'id': [0, 1],
        'code': [111000, 232939],
        'team_h': [3, 5]
    })

    with patch('ingestion.load.vaastav_load.get_latest_fixture_files', return_value=[mock_file]), \
         patch('ingestion.load.vaastav_load.pd.read_parquet', return_value=mock_df), \
         patch('ingestion.load.vaastav_load.get_engine'), \
         patch('pandas.DataFrame.to_sql', autospec=True) as mock_sql:
        
        vaastav_load.load_fixtures_to_postgres()

    mock_sql.assert_called_once()

    # Assert to_sql was called with the correct params
    params = mock_sql.call_args
    df = params.args[0]
    table_name = params.args[1]
    kwargs = params.kwargs

    assert table_name == 'vaastav_fixtures'
    assert kwargs == {'schema': 'raw', 'if_exists': 'append', 'index': False}

    # Assert correct passed DataFrame values
    assert list(df.columns) == ['season', 'fetched_at', 'fixture_season_id', 'raw_data']
    assert (df['season'] == 2026).all()
    assert (df['fetched_at'].dt.strftime('%Y-%m-%d') == '2026-05-01').all()

    assert list(df['fixture_season_id']) == [0, 1]

    first_row_raw_data = json.loads(df['raw_data'].iloc[0])
    assert first_row_raw_data == {'code': 111000, 'team_h': 3}


def test_vaastav_load_fixtures_to_postgres_failure(caplog):
    # Create mock file with correct hierarchy
    mock_file = MagicMock()
    mock_file.parent.name = 'season=2026'
    mock_file.stem = '2026-05-01'

    # Create mock gameweek dataframe
    mock_df = pd.DataFrame({
        'id': [0, 1],
        'code': [111000, 232939],
        'team_h': [3, 5]
    })

    with patch('ingestion.load.vaastav_load.get_latest_fixture_files', return_value=[mock_file]), \
         patch('ingestion.load.vaastav_load.pd.read_parquet', return_value=mock_df), \
         patch('ingestion.load.vaastav_load.get_engine'), \
         patch('pandas.DataFrame.to_sql', autospec=True) as mock_sql, \
         caplog.at_level(logging.ERROR):
        
        mock_sql.side_effect = Exception('Failed to connect')
        vaastav_load.load_fixtures_to_postgres()

    mock_sql.assert_called_once()
    assert 'Failed to connect' in caplog.text


def test_vaastav_load_teams_to_postgres_success():
    # Create mock file with correct hierarchy
    mock_file = MagicMock()
    mock_file.parent.name = 'season=2026'
    mock_file.stem = '2026-05-01'

    # Create mock gameweek dataframe
    mock_df = pd.DataFrame({
        'id': [0, 1],
        'code': [4, 17],
        'name': ['Team A', 'Team B']
    })

    with patch('ingestion.load.vaastav_load.get_latest_team_files', return_value=[mock_file]), \
         patch('ingestion.load.vaastav_load.pd.read_parquet', return_value=mock_df), \
         patch('ingestion.load.vaastav_load.get_engine'), \
         patch('pandas.DataFrame.to_sql', autospec=True) as mock_sql:
        
        vaastav_load.load_teams_to_postgres()

    mock_sql.assert_called_once()

    # Assert to_sql was called with the correct params
    params = mock_sql.call_args
    df = params.args[0]
    table_name = params.args[1]
    kwargs = params.kwargs

    assert table_name == 'vaastav_teams'
    assert kwargs == {'schema': 'raw', 'if_exists': 'append', 'index': False}

    # Assert correct passed DataFrame values
    assert list(df.columns) == ['season', 'team_season_id', 'fetched_at', 'raw_data']
    assert (df['season'] == 2026).all()
    assert (df['fetched_at'].dt.strftime('%Y-%m-%d') == '2026-05-01').all()

    assert list(df['team_season_id']) == [0, 1]

    first_row_raw_data = json.loads(df['raw_data'].iloc[0])
    assert first_row_raw_data == {'code': 4, 'name': 'Team A'}


def test_vaastav_load_teams_to_postgres_failure(caplog):
    # Create mock file with correct hierarchy
    mock_file = MagicMock()
    mock_file.parent.name = 'season=2026'
    mock_file.stem = '2026-05-01'

    # Create mock gameweek dataframe
    mock_df = pd.DataFrame({
        'id': [0, 1],
        'code': [4, 17],
        'name': ['Team A', 'Team B']
    })

    with patch('ingestion.load.vaastav_load.get_latest_team_files', return_value=[mock_file]), \
         patch('ingestion.load.vaastav_load.pd.read_parquet', return_value=mock_df), \
         patch('ingestion.load.vaastav_load.get_engine'), \
         patch('pandas.DataFrame.to_sql', autospec=True) as mock_sql, \
         caplog.at_level(logging.ERROR):
        
        mock_sql.side_effect = Exception('Failed to connect')
        vaastav_load.load_teams_to_postgres()

    mock_sql.assert_called_once()
    assert 'Failed to connect' in caplog.text