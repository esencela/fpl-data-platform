import pytest
import json
import psycopg2
from ingestion.load import fpl_load, vaastav_load, understat_load

@pytest.fixture
def bootstrap_file(tmp_path):
    # Create mock bootstrap json file
    season_dir = tmp_path / 'season=2026'
    season_dir.mkdir()

    file = season_dir / '2026-05-01.json'

    data = {
        'elements': [{'id': 1, 'name': 'Gameweek 1'}, {'id': '2', 'name': 'Gameweek 2'}],
        'events': [{'id': 3, 'web_name': 'Player 3'}, {'id': 4, 'web_name': 'Player 4'}]
    }

    file.write_text(json.dumps(data))

    return file


def test_fpl_load_bootstrap_to_postgres(bootstrap_file, monkeypatch, db_params):
    # Patch mock bootstrap file
    monkeypatch.setattr(
        'ingestion.load.fpl_load.get_latest_bootstrap_file', 
        lambda: bootstrap_file
    )
    
    fpl_load.load_bootstrap_to_postgres(db_params=db_params)

    conn = psycopg2.connect(**db_params)

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT season, raw_data, fetched_at
            FROM raw.fpl_bootstrap_static
            """
        )

        rows = cursor.fetchall()

    conn.close()

    # Assert correct data has been loaded to database
    assert len(rows) == 1

    season, raw_data, fetched_at = rows[0]

    assert season == 2026
    assert fetched_at.strftime('%Y-%m-%d') == '2026-05-01'

    assert raw_data == {
        'elements': [{'id': 1, 'name': 'Gameweek 1'}, {'id': '2', 'name': 'Gameweek 2'}],
        'events': [{'id': 3, 'web_name': 'Player 3'}, {'id': 4, 'web_name': 'Player 4'}]
    }