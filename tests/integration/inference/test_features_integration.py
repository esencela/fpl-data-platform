import pandas as pd
import numpy as np
from inference.features import get_prediction_features


def test_get_prediction_features(features_db):
    df = get_prediction_features(features_db, 'test_schema', 'test_features')

    expected_output = pd.DataFrame({
        'fixture_key': ['fixture_1', 'fixture_2'],
        'player_id': [1, 2],
        'feature_1': ['A', 'B'],
        'feature_2': [0.5, np.nan]
    })

    pd.testing.assert_frame_equal(df, expected_output)
