import json
from unittest.mock import patch, MagicMock
import pytest
from ingestion.load import fpl_load, vaastav_load, understat_load


def test_load_bootstrap_to_postgres_success(tmp_path):
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


def test_load_bootstrap_to_postgres_failure():
    with patch('ingestion.load.fpl_load.get_latest_bootstrap_file') as mock_get, \
         patch('ingestion.load.fpl_load.psycopg2.connect') as mock_conn:        
        
        mock_conn.side_effect = Exception()
        fpl_load.load_bootstrap_to_postgres()

    # Assert bootstrap file is not fetched on connection failure
    mock_conn.assert_called_once()
    mock_get.assert_not_called()


def test_load_element_summaries_to_postgres_success():
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


def test_load_element_summaries_to_postgres_failure():
    with patch('ingestion.load.fpl_load.psycopg2.connect') as mock_conn, \
         patch('ingestion.load.fpl_load.execute_values') as mock_execute:        
        
        mock_conn.side_effect = Exception()
        fpl_load.load_element_summaries_to_postgres()

    # Assert execute values is not called on connection failure
    mock_conn.assert_called_once()
    mock_execute.assert_not_called()


def test_load_fixtures_to_postgres_success(tmp_path):
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


def test_load_fixtures_to_postgres_failure():
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


def test_load_element_summaries_to_postgres_failure():
    with patch('ingestion.load.fpl_load.psycopg2.connect') as mock_conn, \
         patch('ingestion.load.fpl_load.execute_values') as mock_execute:        
        
        mock_conn.side_effect = Exception()
        fpl_load.load_events_to_postgres()

    # Assert execute values is not called on connection failure
    mock_conn.assert_called_once()
    mock_execute.assert_not_called()