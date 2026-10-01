from unittest.mock import patch
import pytest
import pandas as pd
from inference.features import get_prediction_features


def test_get_prediction_features_empty_dataframe():
    # Mock the database connection and return an empty DataFrame
    with patch('inference.features.create_engine') as mock_create_engine, \
         patch('inference.features.pd.read_sql', return_value=pd.DataFrame()) as mock_read_sql:

        with pytest.raises(ValueError, match='No feature rows found'):
            get_prediction_features('mock_db_url', 'mock_schema', 'mock_table')