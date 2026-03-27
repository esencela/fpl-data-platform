import requests
import json
import logging
from pathlib import Path
from datetime import datetime
import asyncio
import aiohttp

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / 'data' / 'raw'

logger = logging.getLogger(__name__)

season = '2026'

def extract_bootstrap():
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
    current_date = datetime.now().strftime('%Y-%m-%d')

    file_path = RAW_DATA_DIR / 'bootstrap-static' / f'season={season}' / f'{current_date}.json'
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    logger.info(f'Bootstrap data saved to {file_path}')


async def extract_element_summaries_async():

    latest_file = get_latest_bootstrap_file()

    with open(latest_file, 'r', encoding='utf-8') as f:
        bootstrap_data = json.load(f)
    
    player_ids = [player['id'] for player in bootstrap_data['elements']]
    
    logger.info(f'Starting extraction for {len(player_ids)} players...')

    # Create base directory for element summaries
    current_date = datetime.now().strftime('%Y-%m-%d')
    base_path = RAW_DATA_DIR / 'element-summary' / f'season={season}' / f'{current_date}'
    base_path.mkdir(parents=True, exist_ok=True)

    # Async fetch with concurrency control
    max_concurrent_requests = 10
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_player(session, semaphore, id, base_path) for id in player_ids]
        await asyncio.gather(*tasks)

    logger.info('Element summary extraction complete.')


def get_latest_bootstrap_file():
    """Returns the path to the most recent bootstrap JSON file."""

    bootstrap_dir = RAW_DATA_DIR / 'bootstrap-static' / f'season={season}'

    file_list = list(bootstrap_dir.glob('*.json'))

    if not file_list:
        raise FileNotFoundError(f'No bootstrap files found in {bootstrap_dir}')
    
    return max(file_list)


async def fetch_player(session, semaphore, player_id, base_path):

    url = f'https://fantasy.premierleague.com/api/element-summary/{player_id}/'

    async with semaphore:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    current_date = datetime.now().strftime('%Y-%m-%d')
                    file_path = base_path / f'player_id={player_id}.json'

                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)

                    logger.info(f'Saved player {player_id}')
                else:
                    logger.warning(f'Failed player {player_id}: {resp.status}')
        except Exception as e:
            logger.error(f'Error fetching player {player_id}: {e}')

        await asyncio.sleep(0.1)  # RATE LIMIT

asyncio.run(extract_element_summaries_async())