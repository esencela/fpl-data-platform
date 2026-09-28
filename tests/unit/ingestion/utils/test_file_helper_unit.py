from unittest.mock import patch, MagicMock
import pytest
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