from unittest.mock import patch, MagicMock
import pytest
import json
from ingestion.utils import fpl_file_helper, vaastav_file_helper, understat_file_helper


def test_get_latest_bootstrap_file_without_season():
    # Season logic, function should call different functions based on season param
    with patch('ingestion.utils.fpl_file_helper.get_latest_path_for_season') as mock_get_season, \
         patch('ingestion.utils.fpl_file_helper.get_latest_path') as mock_get:
        
        fpl_file_helper.get_latest_bootstrap_file()

    mock_get.assert_called_once()
    mock_get_season.assert_not_called()


def test_get_latest_bootstrap_file_with_season():
    # Season logic, function should call different functions based on season param
    with patch('ingestion.utils.fpl_file_helper.get_latest_path_for_season') as mock_get_season, \
         patch('ingestion.utils.fpl_file_helper.get_latest_path') as mock_get:
        
        fpl_file_helper.get_latest_bootstrap_file(season=2026)

    mock_get_season.assert_called_once()
    mock_get.assert_not_called()


def test_get_latest_element_summaries_without_season(tmp_path):
    dir = tmp_path / 'season=2026' / '2026-03-01'
    dir.mkdir(parents=True, exist_ok=True)

    for player_id in [1, 2, 3]:
        data = {'fixtures': '', 'history': ''}

        file = dir / f'player_id={player_id}.json'
        file.write_text(json.dumps(data))

    with patch('ingestion.utils.fpl_file_helper.get_latest_path') as mock_get, \
         patch('ingestion.utils.fpl_file_helper.get_latest_path_for_season') as mock_get_season:
        mock_get.return_value = dir

        output = fpl_file_helper.get_latest_element_summaries()

    expected_output = [
        (2026, 1, json.dumps({'fixtures': '', 'history': ''}), '2026-03-01'),
        (2026, 2, json.dumps({'fixtures': '', 'history': ''}), '2026-03-01'),
        (2026, 3, json.dumps({'fixtures': '', 'history': ''}), '2026-03-01')
    ]

    mock_get.assert_called_once()
    mock_get_season.assert_not_called()
    assert output == expected_output


def test_get_latest_element_summaries_with_season(tmp_path):
    dir = tmp_path / 'season=2026' / '2026-03-01'
    dir.mkdir(parents=True, exist_ok=True)

    for player_id in [1, 2, 3]:
        data = {'fixtures': '', 'history': ''}

        file = dir / f'player_id={player_id}.json'
        file.write_text(json.dumps(data))

    with patch('ingestion.utils.fpl_file_helper.get_latest_path') as mock_get, \
            patch('ingestion.utils.fpl_file_helper.get_latest_path_for_season') as mock_get_season:
        mock_get_season.return_value = dir

        output = fpl_file_helper.get_latest_element_summaries(season=2026)

    expected_output = [
        (2026, 1, json.dumps({'fixtures': '', 'history': ''}), '2026-03-01'),
        (2026, 2, json.dumps({'fixtures': '', 'history': ''}), '2026-03-01'),
        (2026, 3, json.dumps({'fixtures': '', 'history': ''}), '2026-03-01')
    ]

    mock_get_season.assert_called_once()
    mock_get.assert_not_called()
    assert output == expected_output


def test_get_latest_fixtures_file_with_season():
    # Season logic, function should call different functions based on season param
    with patch('ingestion.utils.fpl_file_helper.get_latest_path_for_season') as mock_get_season, \
         patch('ingestion.utils.fpl_file_helper.get_latest_path') as mock_get:
        
        fpl_file_helper.get_latest_fixtures_file()

    mock_get.assert_called_once()
    mock_get_season.assert_not_called()


def test_get_latest_fixtures_file_without_season():
    # Season logic, function should call different functions based on season param
    with patch('ingestion.utils.fpl_file_helper.get_latest_path_for_season') as mock_get_season, \
         patch('ingestion.utils.fpl_file_helper.get_latest_path') as mock_get:
        
        fpl_file_helper.get_latest_fixtures_file(season=2025)

    mock_get_season.assert_called_once()
    mock_get.assert_not_called()
