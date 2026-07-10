import json
import pytest
from unittest.mock import patch, MagicMock
from ingestion.extract import fpl_extract

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

def test_extract_bootstrap_success(tmp_path, mock_bootstrap_response):
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


def test_extract_bootstrap_failure(tmp_path):
    with patch('ingestion.extract.fpl_extract.requests.get') as mock_get, \
         patch.object(fpl_extract, 'FPL_DATA_DIR', tmp_path):
    
        mock_get.return_value.status_code = 500

        # Assert correct exception is raised for failed status code
        with pytest.raises(Exception, match='API request failed with status code 500'):
            fpl_extract.extract_bootstrap()

        # Assert no file was created
        assert not (tmp_path / 'bootstrap-static').exists()


### ASync test


@pytest.fixture
def mock_fixture_response():
    return [
        {"id": 1, "team_h": 1, "team_a": 2, "event": 1},
        {"id": 2, "team_h": 3, "team_a": 4, "event": 2}
    ]

def test_extract_fixtures_success(tmp_path, mock_fixture_response):
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


def test_extract_fixtures_failure(tmp_path):
    with patch('ingestion.extract.fpl_extract.requests.get') as mock_get, \
         patch.object(fpl_extract, 'FPL_DATA_DIR', tmp_path):
    
        mock_get.return_value.status_code = 404

        # Assert correct exception is raised for failed status code
        with pytest.raises(Exception, match='API request failed with status code 404'):
            fpl_extract.extract_fixtures()

        # Assert no file was created
        assert not (tmp_path / 'fixtures').exists()