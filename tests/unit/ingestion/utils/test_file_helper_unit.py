from unittest.mock import patch, MagicMock
import pytest
import json
import pandas as pd
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
    data = {'fixtures': '', 'history': ''}

    for player_id in [1, 2, 3]:
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

    data = {'fixtures': '', 'history': ''}

    for player_id in [1, 2, 3]:
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


def test_get_latest_events_without_season(tmp_path):
    dir = tmp_path / 'season=2026' / '2026-03-01'
    dir.mkdir(parents=True, exist_ok=True)

    data = {'test': '', 'data': ''}

    for id in [1, 2, 3]:
        file = dir / f'gameweek_id={id}.json'
        file.write_text(json.dumps(data))

    with patch('ingestion.utils.fpl_file_helper.get_latest_path') as mock_get, \
         patch('ingestion.utils.fpl_file_helper.get_latest_path_for_season') as mock_get_season:

        mock_get.return_value = dir

        output = fpl_file_helper.get_latest_events()

    expected_output = [
        (2026, 1, json.dumps({'test': '', 'data': ''}), '2026-03-01'),
        (2026, 2, json.dumps({'test': '', 'data': ''}), '2026-03-01'),
        (2026, 3, json.dumps({'test': '', 'data': ''}), '2026-03-01')
    ]

    mock_get.assert_called_once()
    mock_get_season.assert_not_called()
    assert output == expected_output


def test_get_latest_events_with_season(tmp_path):
    dir = tmp_path / 'season=2026' / '2026-03-01'
    dir.mkdir(parents=True, exist_ok=True)

    data = {'test': '', 'data': ''}

    for id in [1, 2, 3]:
        file = dir / f'gameweek_id={id}.json'
        file.write_text(json.dumps(data))

    with patch('ingestion.utils.fpl_file_helper.get_latest_path') as mock_get, \
         patch('ingestion.utils.fpl_file_helper.get_latest_path_for_season') as mock_get_season:

        mock_get_season.return_value = dir

        output = fpl_file_helper.get_latest_events(season=2026)

    expected_output = [
        (2026, 1, json.dumps({'test': '', 'data': ''}), '2026-03-01'),
        (2026, 2, json.dumps({'test': '', 'data': ''}), '2026-03-01'),
        (2026, 3, json.dumps({'test': '', 'data': ''}), '2026-03-01')
    ]

    mock_get_season.assert_called_once()
    mock_get.assert_not_called()
    assert output == expected_output


def test_get_latest_match_files(tmp_path):
    dir = tmp_path / 'matches'
    dir.mkdir(parents=True, exist_ok=True)

    data = {'test': '', 'data': ''}

    for id in [1, 2, 3]:
        file = dir / f'match_id={id}.json'
        file.write_text(json.dumps(data))

    with patch.object(understat_file_helper, 'UNDERSTAT_DATA_DIR', tmp_path):
        output = understat_file_helper.get_latest_match_files()

    expected_output = [
        (1, json.dumps(data)),
        (2, json.dumps(data)),
        (3, json.dumps(data))
    ]

    print(output)
    print(expected_output)

    assert output == expected_output


def test_get_latest_id_mappings_file_success(tmp_path):
    dir = tmp_path / 'id_mappings'
    dir.mkdir(parents=True, exist_ok=True)

    for date in ['2026-04-03', '2026-01-02', '2027-01-01']:
        file = dir / f'{date}.parquet'

        df = pd.DataFrame({'test': [1]})

        df.to_parquet(file)

    with patch.object(understat_file_helper, 'UNDERSTAT_DATA_DIR', tmp_path):
        output = understat_file_helper.get_latest_id_mappings_file()

    assert output == dir / '2027-01-01.parquet'


def test_get_latest_id_mappings_file_empty_folder(tmp_path):
    dir = tmp_path / 'id_mappings'
    dir.mkdir(parents=True, exist_ok=True)

    with patch.object(understat_file_helper, 'UNDERSTAT_DATA_DIR', tmp_path), \
         pytest.raises(FileNotFoundError, match='No ID mappings files'):
        understat_file_helper.get_latest_id_mappings_file()