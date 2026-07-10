import json
from urllib.error import HTTPError
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from ingestion.extract import fpl_extract, vaastav_extract, understat_extract

@pytest.fixture
def mock_bootstrap_response():
    return {
        "elements": [
            {"id": 1, "first_name": "Player", "second_name": "One"},
            {"id": 2, "first_name": "Player", "second_name": "Two"}
        ],
        "events": [
            {"id": 1, "name": "Gameweek 1"},
            {"id": 2, "name": "Gameweek 2"}
        ]
    }

def test_fpl_extract_bootstrap_success(tmp_path, mock_bootstrap_response):
    with patch('ingestion.extract.fpl_extract.requests.get') as mock_get, \
         patch.object(fpl_extract, 'FPL_DATA_DIR', tmp_path), \
         patch.object(fpl_extract, 'CURRENT_DATE', '2026-05-01'), \
         patch.object(fpl_extract.settings, 'CURRENT_SEASON', 2026):
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_bootstrap_response

        fpl_extract.extract_bootstrap()

        # Assert file was created at expected path
        expected_file_path = tmp_path / 'bootstrap-static' / 'season=2026' / '2026-05-01.json'
        assert expected_file_path.exists()

        # Assert content matches mock response
        with open(expected_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert data == mock_bootstrap_response


def test_fpl_extract_bootstrap_failure(tmp_path):
    with patch('ingestion.extract.fpl_extract.requests.get') as mock_get, \
         patch.object(fpl_extract, 'FPL_DATA_DIR', tmp_path):
    
        mock_get.return_value.status_code = 500

        # Assert correct exception is raised for failed status code
        with pytest.raises(Exception, match='API request failed with status code 500'):
            fpl_extract.extract_bootstrap()

        # Assert no file was created
        assert not (tmp_path / 'bootstrap-static').exists()


### ASync test element summary and player


@pytest.fixture
def mock_fixture_response():
    return [
        {"id": 1, "team_h": 1, "team_a": 2, "event": 1},
        {"id": 2, "team_h": 3, "team_a": 4, "event": 2}
    ]

def test_fpl_extract_fixtures_success(tmp_path, mock_fixture_response):
    with patch('ingestion.extract.fpl_extract.requests.get') as mock_get, \
         patch.object(fpl_extract, 'FPL_DATA_DIR', tmp_path), \
         patch.object(fpl_extract, 'CURRENT_DATE', '2026-05-01'), \
         patch.object(fpl_extract.settings, 'CURRENT_SEASON', 2026):
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_fixture_response

        fpl_extract.extract_fixtures()

        # Assert file was created at expected path
        expected_file_path = tmp_path / 'fixtures' / 'season=2026' / '2026-05-01.json'
        assert expected_file_path.exists()

        # Assert content matches mock response
        with open(expected_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert data == mock_fixture_response


def test_fpl_extract_fixtures_failure(tmp_path):
    with patch('ingestion.extract.fpl_extract.requests.get') as mock_get, \
         patch.object(fpl_extract, 'FPL_DATA_DIR', tmp_path):
    
        mock_get.return_value.status_code = 404

        # Assert correct exception is raised for failed status code
        with pytest.raises(Exception, match='API request failed with status code 404'):
            fpl_extract.extract_fixtures()

        # Assert no file was created
        assert not (tmp_path / 'fixtures').exists()


### Async test events and gameweeks


def test_get_season_string():
    assert vaastav_extract.get_season_string(2023) == '2022-23'
    assert vaastav_extract.get_season_string(2000) == '1999-00'


def mock_vaastav_player_dataframe():
    return pd.DataFrame({
        'player_id': [1, 2],
        'name': ['Player One', 'Player Two'],
        'team': ['Team A', 'Team B']
    })


def test_vaastav_extract_player_data_success(tmp_path):
    with patch('ingestion.extract.vaastav_extract.pd.read_csv') as mock_df, \
         patch.object(vaastav_extract, 'VAASTAV_DATA_DIR', tmp_path), \
         patch.object(vaastav_extract, 'CURRENT_DATE', '2026-05-01'):
        
        mock_df.return_value = mock_vaastav_player_dataframe()

        vaastav_extract.extract_player_data()

        # Assert file was created at expected path
        for _, season in vaastav_extract.seasons:
            expected_file_path = tmp_path / 'players' / f'season={season}' / '2026-05-01.parquet'
            assert expected_file_path.exists()

            # Assert content matches mock response
            df = pd.read_parquet(expected_file_path)
            assert df.equals(mock_vaastav_player_dataframe())


def test_vaastav_extract_player_data_failure(tmp_path):
    with patch('ingestion.extract.vaastav_extract.pd.read_csv') as mock_df, \
         patch.object(vaastav_extract, 'VAASTAV_DATA_DIR', tmp_path):
        
        mock_df.side_effect = Exception('Failed to retrieve player data')

        # Assert correct exception is raised
        with pytest.raises(Exception, match='Failed to retrieve player data'):
            vaastav_extract.extract_player_data()

        # Assert no file was created
        expected_file_path = tmp_path / 'players'
        assert not expected_file_path.exists()


def mock_vaastav_gameweek_dataframe():
    return pd.DataFrame({
        'player_id': [1, 2],
        'gameweek': [1, 2],
        'points': [5, 10]
    })


def test_vaastav_extract_gameweek_data_success(tmp_path):
    with patch('ingestion.extract.vaastav_extract.pd.read_csv') as mock_df, \
         patch.object(vaastav_extract, 'VAASTAV_DATA_DIR', tmp_path), \
         patch.object(vaastav_extract, 'CURRENT_DATE', '2026-05-01'):

        mock_df.return_value = mock_vaastav_gameweek_dataframe()

        vaastav_extract.extract_gameweek_data()

        # Assert file was created at expected path
        for _, season in vaastav_extract.seasons:
            expected_file_path = tmp_path / 'gws' / f'season={season}' / '2026-05-01.parquet'
            assert expected_file_path.exists()

            # Assert content matches mock response
            df = pd.read_parquet(expected_file_path)
            assert df.equals(mock_vaastav_gameweek_dataframe())


def test_vaastav_extract_gameweek_data_failure(tmp_path):
    with patch('ingestion.extract.vaastav_extract.pd.read_csv') as mock_df, \
         patch.object(vaastav_extract, 'VAASTAV_DATA_DIR', tmp_path):
        
        mock_df.side_effect = Exception('Failed to retrieve gameweek data')

        # Assert correct exception is raised
        with pytest.raises(Exception, match='Failed to retrieve gameweek data'):
            vaastav_extract.extract_gameweek_data()

        # Assert no file was created
        expected_file_path = tmp_path / 'gws'
        assert not expected_file_path.exists()


def mock_vaastav_fixture_dataframe():
    return pd.DataFrame({
        'fixture_id': [1, 2],
        'home_team': ['Team A', 'Team B'],
        'away_team': ['Team C', 'Team D']
    })


def test_vaastav_extract_fixture_data_success(tmp_path):
    with patch('ingestion.extract.vaastav_extract.pd.read_csv') as mock_df, \
         patch.object(vaastav_extract, 'VAASTAV_DATA_DIR', tmp_path), \
         patch.object(vaastav_extract, 'CURRENT_DATE', '2026-05-01'):
        
        mock_df.return_value = mock_vaastav_fixture_dataframe()

        vaastav_extract.extract_fixture_data()

        # Assert file was created at expected path
        for _, season in vaastav_extract.seasons:
            expected_file_path = tmp_path / 'fixtures' / f'season={season}' / '2026-05-01.parquet'
            assert expected_file_path.exists()

            # Assert content matches mock response
            df = pd.read_parquet(expected_file_path)
            assert df.equals(mock_vaastav_fixture_dataframe())


def test_vaastav_extract_fixture_data_failure(tmp_path):
    with patch('ingestion.extract.vaastav_extract.pd.read_csv') as mock_df, \
         patch.object(vaastav_extract, 'VAASTAV_DATA_DIR', tmp_path):
        
        mock_df.side_effect = Exception('Failed to retrieve fixture data')

        # Assert correct exception is raised
        with pytest.raises(Exception, match='Failed to retrieve fixture data'):
            vaastav_extract.extract_fixture_data()

        # Create HTTPError with 500 error - function will ignore 404 errors
        mock_df.side_effect = HTTPError(url='https://example.com', code=500, msg='Internal Server Error', hdrs=None, fp=None)

        # Assert correct exception is raised for HTTPError
        with pytest.raises(HTTPError, match='HTTP Error 500: Internal Server Error'):
            vaastav_extract.extract_fixture_data()

        # Assert no file was created
        expected_file_path = tmp_path / 'fixtures'
        assert not expected_file_path.exists()


def mock_vaastav_team_dataframe():
    return pd.DataFrame({
        'team_id': [1, 2],
        'team_name': ['Team A', 'Team B']
    })


def test_vaastav_extract_team_data_success(tmp_path):
    with patch('ingestion.extract.vaastav_extract.pd.read_csv') as mock_df, \
         patch.object(vaastav_extract, 'VAASTAV_DATA_DIR', tmp_path), \
         patch.object(vaastav_extract, 'CURRENT_DATE', '2026-05-01'):
        
        mock_df.return_value = mock_vaastav_team_dataframe()

        vaastav_extract.extract_team_data()

        # Assert file was created at expected path
        for _, season in vaastav_extract.seasons:
            expected_file_path = tmp_path / 'teams' / f'season={season}' / '2026-05-01.parquet'
            assert expected_file_path.exists()

            # Assert content matches mock response
            df = pd.read_parquet(expected_file_path)
            assert df.equals(mock_vaastav_team_dataframe())


def test_vaastav_extract_team_data_failure(tmp_path):
    with patch('ingestion.extract.vaastav_extract.pd.read_csv') as mock_df, \
         patch.object(vaastav_extract, 'VAASTAV_DATA_DIR', tmp_path):
        
        mock_df.side_effect = Exception('Failed to retrieve team data')

        # Assert correct exception is raised
        with pytest.raises(Exception, match='Failed to retrieve team data'):
            vaastav_extract.extract_team_data()

        # Create HTTPError with 500 error - function will ignore 404 errors
        mock_df.side_effect = HTTPError(url='https://example.com', code=500, msg='Internal Server Error', hdrs=None, fp=None)

        # Assert correct exception is raised for HTTPError
        with pytest.raises(HTTPError, match='HTTP Error 500: Internal Server Error'):
            vaastav_extract.extract_team_data()

        # Assert no file was created
        expected_file_path = tmp_path / 'teams'
        assert not expected_file_path.exists()