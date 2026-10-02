from unittest.mock import patch, MagicMock
import pytest
import pandas as pd
from inference.predict import predict
from inference.model_store import ModelMeta


def metadata():
    # Returns a sample metadata dictionary for testing purposes.
    return {
        'model_name': 'test_model',
        'model_version': '1.0',
        'target': 'target_variable',
        'feature_columns': ['feature1', 'feature2'],
        'categorical_columns': ['feature1'],
        'category_maps': {'feature1': ['A', 'B', 'C']},
        'trained_through_season': 2023,
        'trained_at': '2023-01-01T00:00:00Z',
        'framework': 'lightgbm',
        'framework_version': '3.3.2'
    }


def features():
    # Returns a sample features DataFrame for testing purposes.
    return pd.DataFrame({
        'fixture_key': [1, 2],
        'player_id': [101, 102],
        'feature1': ['A', 'B'],
        'feature2': [0.5, 0.8]
    })


def test_predict_success():
    # Mock model and prediction output
    mock_model = MagicMock()
    mock_model.predict.return_value = [0.1, 0.9]

    meta = ModelMeta(**metadata())

    df_features = features()

    predictions = predict(df_features, mock_model, meta)

    # Assert predict called with correct features
    mock_model.predict.assert_called_once()
    args = mock_model.predict.call_args[0]

    expected_model_input = pd.DataFrame({
        'feature1': pd.Categorical(['A', 'B'], categories=['A', 'B', 'C']),
        'feature2': [0.5, 0.8]
    })

    pd.testing.assert_frame_equal(args[0], expected_model_input)

    # Assert the predictions DataFrame has the expected structure and values
    expected_output = pd.DataFrame({
        'fixture_key': [1, 2],
        'player_id': [101, 102],
        'target': ['target_variable', 'target_variable'],
        'predicted_value': [0.1, 0.9],
        'model_name': ['test_model', 'test_model'],
        'model_version': ['1.0', '1.0']
    })

    pd.testing.assert_frame_equal(predictions, expected_output)


def test_predict_missing_id_column():
    mock_model = MagicMock()
    meta = ModelMeta(**metadata())

    # Drop required ID column from features DataFrame
    df_features = features().drop(columns=['fixture_key'])

    with pytest.raises(ValueError, match='Feature table is missing column'):
        predict(df_features, mock_model, meta)


def test_predict_missing_feature_column():
    mock_model = MagicMock()
    meta = ModelMeta(**metadata())

    # Drop required feature column from features DataFrame
    df_features = features().drop(columns=['feature1'])

    with pytest.raises(ValueError, match='Feature table is missing feature'):
        predict(df_features, mock_model, meta)