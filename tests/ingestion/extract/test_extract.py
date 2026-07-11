import json
import asyncio
from urllib.error import HTTPError
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
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


def mock_aiohttp_response(json_data, status=200):
    """Mock aiohttp response usable as an async context manager."""

    mock_response = MagicMock()
    mock_response.status = status
    mock_response.json = AsyncMock(return_value=json_data)

    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context_manager.__aexit__ = AsyncMock(return_value=False)

    return mock_context_manager


async def test_fetch_player_async_success(tmp_path):
    player_data = {"id": 1, "first_name": "Player", "second_name": "One"}

    mock_context_manager = mock_aiohttp_response(player_data, status=200)

    mock_session = MagicMock()
    mock_session.get.return_value = mock_context_manager

    semaphore = asyncio.Semaphore(10)

    with patch.object(fpl_extract, 'RATE_LIMIT', 0): # Set rate limit to 0 for testing
        await fpl_extract.fetch_player_async(
            session=mock_session, 
            semaphore=semaphore,
            player_id=1, 
            base_path=tmp_path)
        
    mock_session.get.assert_called_once_with('https://fantasy.premierleague.com/api/element-summary/1/')

    expected_file_path = tmp_path / 'player_id=1.json'
    assert expected_file_path.exists()

    with open(expected_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert data == player_data


async def test_fetch_player_async_failure(tmp_path):
    mock_context_manager = mock_aiohttp_response({}, status=404)

    mock_session = MagicMock()
    mock_session.get.return_value = mock_context_manager

    semaphore = asyncio.Semaphore(10)

    with patch.object(fpl_extract, 'RATE_LIMIT', 0): # Set rate limit to 0 for testing
        await fpl_extract.fetch_player_async(
            session=mock_session, 
            semaphore=semaphore,
            player_id=1, 
            base_path=tmp_path)
        
    # Assert no file was created
    assert not (tmp_path / 'player_id=1.json').exists()


async def test_extract_element_summaries_async(tmp_path, mock_bootstrap_response):
    bootstrap_file = tmp_path / 'bootstrap.json'
    bootstrap_file.write_text(json.dumps(mock_bootstrap_response))

    with patch.object(fpl_extract, 'FPL_DATA_DIR', tmp_path), \
         patch.object(fpl_extract.settings, 'CURRENT_SEASON', 2026), \
         patch.object(fpl_extract, 'CURRENT_DATE', '2026-05-01'), \
         patch('ingestion.extract.fpl_extract.get_latest_bootstrap_file', return_value=bootstrap_file), \
         patch('ingestion.extract.fpl_extract.fetch_player_async', new=AsyncMock()) as mock_fetch_player, \
         patch('ingestion.extract.fpl_extract.aiohttp.ClientSession'):

        await fpl_extract.extract_element_summaries_async()

    assert mock_fetch_player.call_count == len(mock_bootstrap_response['elements'])


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
def test_fetch_gameweek_async_success(tmp_path):
    gameweek_data = {"id": 1, "name": "Gameweek 1"}

    mock_context_manager = mock_aiohttp_response(gameweek_data, status=200)

    mock_session = MagicMock()
    mock_session.get.return_value = mock_context_manager

    semaphore = asyncio.Semaphore(10)

    with patch.object(fpl_extract, 'RATE_LIMIT', 0): # Set rate limit to 0 for testing
        asyncio.run(fpl_extract.fetch_gameweek_async(
            session=mock_session, 
            semaphore=semaphore,
            gameweek_id=1, 
            base_path=tmp_path))

    mock_session.get.assert_called_once_with('https://fantasy.premierleague.com/api/event/1/live/')

    expected_file_path = tmp_path / 'gameweek=1.json'
    assert expected_file_path.exists()

    with open(expected_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert data == gameweek_data


def test_fetch_gameweek_async_failure(tmp_path):
    mock_context_manager = mock_aiohttp_response({}, status=404)

    mock_session = MagicMock()
    mock_session.get.return_value = mock_context_manager

    semaphore = asyncio.Semaphore(10)

    with patch.object(fpl_extract, 'RATE_LIMIT', 0): # Set rate limit to 0 for testing
        asyncio.run(fpl_extract.fetch_gameweek_async(
            session=mock_session, 
            semaphore=semaphore,
            gameweek_id=1, 
            base_path=tmp_path))

    # Assert no file was created
    assert not (tmp_path / 'gameweek=1.json').exists()


def test_extract_events_async(tmp_path, mock_bootstrap_response):
    bootstrap_file = tmp_path / 'bootstrap.json'
    bootstrap_file.write_text(json.dumps(mock_bootstrap_response))

    with patch.object(fpl_extract, 'FPL_DATA_DIR', tmp_path), \
         patch.object(fpl_extract.settings, 'CURRENT_SEASON', 2026), \
         patch.object(fpl_extract, 'CURRENT_DATE', '2026-05-01'), \
         patch('ingestion.extract.fpl_extract.get_latest_bootstrap_file', return_value=bootstrap_file), \
         patch('ingestion.extract.fpl_extract.fetch_gameweek_async', new=AsyncMock()) as mock_fetch_gameweek, \
         patch('ingestion.extract.fpl_extract.aiohttp.ClientSession'):
        
        asyncio.run(fpl_extract.extract_events_async())

    assert mock_fetch_gameweek.call_count == len(mock_bootstrap_response['events'])


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


def test_get_understat_season():
    assert understat_extract.get_understat_season(2023) == '2022'
    assert understat_extract.get_understat_season(2000) == '1999'


def mock_understat_season_data():
    return {
        'season': '2026',
        'data': 'mock_season_data'
    }


def test_understat_extract_season_data_success(tmp_path):
    with patch('ingestion.extract.understat_extract.client.league') as mock_league, \
         patch.object(understat_extract, 'UNDERSTAT_DATA_DIR', tmp_path), \
         patch.object(understat_extract, 'CURRENT_DATE', '2026-05-01'), \
         patch.object(understat_extract.settings, 'CURRENT_SEASON', 2026):
        
        mock_league.return_value._get_data.return_value = mock_understat_season_data()

        understat_extract.extract_season_data()

        # Assert file was created at expected path
        expected_file_path = tmp_path / 'season_data' / 'season=2026' / '2026-05-01.json'
        assert expected_file_path.exists()

        # Assert content matches mock response
        with open(expected_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert data == mock_understat_season_data()


def test_understat_extract_season_data_failure(tmp_path):
    with patch('ingestion.extract.understat_extract.client.league') as mock_league, \
         patch.object(understat_extract, 'UNDERSTAT_DATA_DIR', tmp_path):
        
        mock_league.return_value._get_data.side_effect = Exception('Failed to retrieve season data')

        # Assert correct exception is raised
        with pytest.raises(Exception, match='Failed to retrieve season data'):
            understat_extract.extract_season_data()

        # Assert no file was created
        expected_file_path = tmp_path / 'season_data'
        assert not expected_file_path.exists()


### Add more understat tests