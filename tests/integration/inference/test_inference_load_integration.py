import pandas as pd
from inference.load import load_predictions
from sqlalchemy import create_engine, text


def test_load_predictions(predictions_db):
    # Sample predictions DataFrame
    df_predictions = pd.DataFrame({
        'fixture_key': ['2026_1', '2026_2'],
        'player_id': [1, 2],
        'model_name': ['test_model', 'test_model'],
        'model_version': ['v1', 'v1'],
        'target': ['target_1', 'target_1'],
        'predicted_value': [0.8, 0.6]
    })

    load_predictions(predictions_db, 'test_schema', 'test_predictions', df_predictions)

    # Verify that the predictions were loaded correctly
    engine = create_engine(predictions_db)
    with engine.begin() as conn:
        query = text('SELECT * FROM test_schema.test_predictions')
        loaded_predictions = pd.read_sql(query, conn)

    pd.testing.assert_frame_equal(df_predictions, loaded_predictions)