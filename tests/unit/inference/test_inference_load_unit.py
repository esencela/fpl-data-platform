import pandas as pd
from unittest.mock import patch, MagicMock
from inference.load import load_predictions


def test_load_predictions_success():
    # Sample predictions DataFrame
    predictions = pd.DataFrame({
        'fixture_key': [1, 2],
        'player_id': [101, 102],
        'target': ['target_variable', 'target_variable'],
        'predicted_value': [0.1, 0.9],
        'model_name': ['test_model', 'test_model'],
        'model_version': ['1.0', '1.0']
    })

    # Mock the SQLAlchemy engine and connection
    mock_db_url = 'postgresql://user:password@localhost/testdb'
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_engine.begin.return_value.__enter__.return_value = mock_conn

    with patch('inference.load.create_engine', return_value=mock_engine), \
         patch.object(predictions, 'to_sql') as mock_to_sql:
        
        load_predictions(mock_db_url, 'public', 'predictions_table', predictions)

    # Check that the DELETE query was executed with the correct parameters
    mock_conn.execute.assert_called_once()
    args = mock_conn.execute.call_args[0]

    sql_text, params = args

    assert 'DELETE FROM public.predictions_table' in str(sql_text)

    assert params['model_name'] == 'test_model'
    assert params['model_version'] == '1.0'
    assert params['target'] == 'target_variable'

    # Check that to_sql was called with the correct parameters
    mock_to_sql.assert_called_once_with('predictions_table', mock_conn, schema='public', if_exists='append', index=False)