import json
from pathlib import Path
from config import CURRENT_SEASON

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / 'data' / 'raw'

def get_latest_bootstrap_file():
    """Returns the path to the most recent bootstrap JSON file."""

    bootstrap_dir = RAW_DATA_DIR / 'bootstrap-static' / f'season={CURRENT_SEASON}'

    file_list = list(bootstrap_dir.glob('*.json'))

    if not file_list:
        raise FileNotFoundError(f'No bootstrap files found in {bootstrap_dir}')
    
    return max(file_list)


def get_latest_element_summaries():
    """Returns a list of records from the most recent element summary JSON files."""
    
    element_summary_dir = RAW_DATA_DIR / 'element-summary' / f'season={CURRENT_SEASON}'

    file_list = list(element_summary_dir.glob('*'))

    if not file_list:
        raise FileNotFoundError(f'Folder is empty: {element_summary_dir}')
    
    # Folder structure example: element-summary/season=2026/2024-08-01/player_id=123.json
    latest_date = max(file.stem for file in file_list)
    latest_folder = element_summary_dir / latest_date

    elements = []
    for file in latest_folder.glob('*.json'):
        player_id = int(file.stem.split('=')[1])
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            elements.append((CURRENT_SEASON, player_id, json.dumps(data), latest_date))

    return elements