import requests
import json
import logging
from pathlib import Path
from datetime import datetime
import asyncio
import aiohttp
from utils.files import get_latest_bootstrap_file
from config import CURRENT_SEASON

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / 'data' / 'raw'

CURRENT_DATE = datetime.now().strftime('%Y-%m-%d')

RATE_LIMIT = 0.1  # seconds between requests to avoid hitting API rate 

logger = logging.getLogger(__name__)
# logger.setLevel(level=logging.INFO)
# 
# handler = logging.StreamHandler()
# handler.setLevel(logging.INFO)
# 
# logger.addHandler(handler)


def extract_bootstrap() -> None:
    """Extracts bootstrap data from the FPL API and saves it to a JSON file."""

    api_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'

    logger.info('Extracting bootstrap data from API...')

    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        logger.info('Bootstrap data extracted successfully.')
    else:
        logger.error('Failed to extract bootstrap data.')
        raise Exception(f'API request failed with status code {response.status_code}')
    
    # Save the extracted data to a JSON file named with the current date
    file_path = RAW_DATA_DIR / 'bootstrap-static' / f'season={CURRENT_SEASON}' / f'{CURRENT_DATE}.json'
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    logger.info(f'Bootstrap data saved to {file_path}')


async def extract_element_summaries_async() -> None:
    """Extracts element summary data (player data) asynchronously and saves each to a separate JSON file."""

    latest_file = get_latest_bootstrap_file()

    with open(latest_file, 'r', encoding='utf-8') as f:
        bootstrap_data = json.load(f)
    
    player_ids = [player['id'] for player in bootstrap_data['elements']]
    
    logger.info(f'Starting extraction for {len(player_ids)} players...')

    # Create base directory for element summaries
    base_path = RAW_DATA_DIR / 'element-summary' / f'season={CURRENT_SEASON}' / f'{CURRENT_DATE}'
    base_path.mkdir(parents=True, exist_ok=True)

    # Async fetch with concurrency control
    max_concurrent_requests = 10
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_player_async(session, semaphore, id, base_path) for id in player_ids]
        await asyncio.gather(*tasks)

    logger.info('Element summary extraction complete.')


async def fetch_player_async(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, player_id: int, base_path: Path) -> None:
    """
    Fetches the element summary for a single player and saves it to a JSON file.

    Params:
        session(aiohttp.ClientSession): The aiohttp client session to use for the request.
        semaphore(asyncio.Semaphore): The asyncio semaphore to control concurrency.
        player_id(int): The ID of the player to fetch.
        base_path(pathlib.Path): The base directory where the player JSON file should be saved.
    """
    
    url = f'https://fantasy.premierleague.com/api/element-summary/{player_id}/'

    async with semaphore:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    file_path = base_path / f'player_id={player_id}.json'

                    with open(file_path, 'w', encoding='utf-8') as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    logger.info(f'Saved player {player_id}')
                else:
                    logger.warning(f'Failed player {player_id}: {response.status}')
        except Exception as e:
            logger.error(f'Error fetching player {player_id}: {e}')

        await asyncio.sleep(RATE_LIMIT)


def extract_fixtures() -> None:
    """Extracts fixture data from the FPL API and saves it to a JSON file."""

    api_url = 'https://fantasy.premierleague.com/api/fixtures/'

    logger.info('Extracting fixture data from API...')

    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        logger.info('Fixture data extracted successfully.')
    else:
        logger.error('Failed to extract fixture data.')
        raise Exception(f'API request failed with status code {response.status_code}')
    
    # Save the extracted data to a JSON file named with the current date
    file_path = RAW_DATA_DIR / 'fixtures' / f'season={CURRENT_SEASON}' / f'{CURRENT_DATE}.json'
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    logger.info(f'Fixture data saved to {file_path}')


async def extract_events_async():
    """Extracts event data (gameweek data) asynchronously and saves each to a separate JSON file."""

    latest_file = get_latest_bootstrap_file()

    with open(latest_file, 'r', encoding='utf-8') as f:
        bootstrap_data = json.load(f)

    gameweek_ids = [gameweek['id'] for gameweek in bootstrap_data['events']]
    
    logger.info(f'Starting extraction for {len(gameweek_ids)} gameweeks...')

    # Create base directory for event summaries
    base_path = RAW_DATA_DIR / 'events' / f'season={CURRENT_SEASON}' / f'{CURRENT_DATE}'
    base_path.mkdir(parents=True, exist_ok=True)

    # Async fetch with concurrency control
    max_concurrent_requests = 10
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_gameweek_async(session, semaphore, id, base_path) for id in gameweek_ids]
        await asyncio.gather(*tasks)

    logger.info('Event summary extraction complete.')


async def fetch_gameweek_async(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, gameweek_id: int, base_path: Path) -> None:
    """
    Fetches the event summary for a single gameweek and saves it to a JSON file.

    Params:
        session(aiohttp.ClientSession): The aiohttp client session to use for the request.
        semaphore(asyncio.Semaphore): The asyncio semaphore to control concurrency.
        gameweek_id(int): The ID of the gameweek to fetch.
        base_path(pathlib.Path): The base directory where the gameweek JSON file should be saved.
    """

    url = f'https://fantasy.premierleague.com/api/event/{gameweek_id}/live/'

    async with semaphore:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    file_path = base_path / f'gameweek={gameweek_id}.json'

                    with open(file_path, 'w', encoding='utf-8') as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)

                    logger.info(f'Saved gameweek {gameweek_id}')
                else:
                    logger.warning(f'Failed gameweek {gameweek_id}: {response.status}')
        except Exception as e:
            logger.error(f'Error fetching gameweek {gameweek_id}: {e}')

        await asyncio.sleep(RATE_LIMIT)