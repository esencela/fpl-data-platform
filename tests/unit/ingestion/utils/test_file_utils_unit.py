from unittest.mock import patch, MagicMock
from ingestion.utils import file_utils
import logging
import pytest


def test_get_latest_season_folder_success(tmp_path):
    # Create season folders, function should return most recent
    for season in [2026, 2025]:
        dir = tmp_path / f'season={season}'
        dir.mkdir(exist_ok=True)

    result = file_utils.get_latest_season_folder(tmp_path)

    assert result == tmp_path / 'season=2026'


def test_get_latest_season_folder_empty_folder(tmp_path):
    # Empty folder should raise error
    with pytest.raises(FileNotFoundError):
        file_utils.get_latest_season_folder(tmp_path)


def test_get_latest_path_no_file_type_success(tmp_path):
    # Create season paths with dates, function should return path with latest date
    for season, dates in [(2026, ['2026-05-04', '2026-01-02', '2025-11-12']), (2025, ['2025-01-02'])]:
        for date in dates:
            dir = tmp_path / f'season={season}'
            dir.mkdir(exist_ok=True)

            file = dir / f'{date}.json'
            file.write_text('{}')

    result = file_utils.get_latest_path(tmp_path)

    assert result == tmp_path / 'season=2026' / '2026-05-04.json'


def test_get_latest_path_with_file_type_success(tmp_path):
    # Create season paths with dates, function should only return specified file types
    for file in ['2026-05-04.txt', '2026-01-02.json', '2025-11-12.txt', '2025-11-11.json']:
        dir = tmp_path / 'season=2026'
        dir.mkdir(exist_ok=True)

        f = dir / file
        f.write_text('{}')

    result = file_utils.get_latest_path(tmp_path, '.json')

    assert result == tmp_path / 'season=2026' / '2026-01-02.json'


def test_get_latest_path_empty_folder(tmp_path):
    # Empty season folder should raise error
    dir = tmp_path / 'season=2026'
    dir.mkdir(exist_ok=True)

    with pytest.raises(FileNotFoundError):
        file_utils.get_latest_path(tmp_path)


def test_get_latest_path_for_season_success(tmp_path):
    # Create season paths with dates, function should return path with latest date in specified season
    for season, dates in [(2026, ['2026-05-04', '2026-01-02']), (2025, ['2025-01-02', '2024-11-01'])]:
        for date in dates:
            dir = tmp_path / f'season={season}'
            dir.mkdir(exist_ok=True)

            file = dir / f'{date}.json'
            file.write_text('{}')

    result = file_utils.get_latest_path_for_season(tmp_path, season=2025)

    assert result == tmp_path / 'season=2025' / '2025-01-02.json'


def test_get_latest_path_missing_season_folder(tmp_path):
    # Create folder paths, missing season folder should raise error
    for season in [2025, 2024]:
        dir = tmp_path / f'season={season}'
        dir.mkdir(exist_ok=True)

    with pytest.raises(FileNotFoundError, match='Season folder not found'):
        file_utils.get_latest_path_for_season(tmp_path, season=2026)


def test_get_latest_path_empty_season_folder(tmp_path):
    # Create folder paths, empty season folder should raise error
    dir = tmp_path / 'season=2026'
    dir.mkdir(exist_ok=True)

    with pytest.raises(FileNotFoundError, match='No files found in directory'):
        file_utils.get_latest_path_for_season(tmp_path, season=2026)


def test_get_latest_file_for_each_season_success(tmp_path):
    # Create folder paths, function should return an array of files with latest date from each season
    for season, files in [(2026, ['2026-05-04.txt', '2026-01-02.json']), (2025, ['2025-01-02.json', '2024-11-01.json'])]:
        for file in files:
            dir = tmp_path / f'season={season}'
            dir.mkdir(exist_ok=True)

            f = dir / file
            f.write_text('{}')

    result = file_utils.get_latest_file_for_each_season(tmp_path, file_type='.json')

    assert tmp_path / 'season=2026' / '2026-01-02.json' in result
    assert tmp_path / 'season=2025' / '2025-01-02.json' in result
    assert len(result) == 2


def test_get_latest_file_for_each_season_missing_file_type(tmp_path):
    # No specified file type should raise error
    with pytest.raises(TypeError):
        file_utils.get_latest_file_for_each_season(tmp_path)


def test_get_latest_file_for_each_season_empty_folder(tmp_path):
    # Create folder paths, empty season folder should raise error
    dir = tmp_path / 'season=2026'
    dir.mkdir(exist_ok=True)

    with pytest.raises(FileNotFoundError, match='File not found in directory'):
        file_utils.get_latest_file_for_each_season(tmp_path, file_type='.json')