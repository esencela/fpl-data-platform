import pandas as pd
from inference.model_store import ModelMeta

REQUIRED_ID_COLUMNS = ['fixture_key', 'player_id']

def predict(features: pd.DataFrame, model, meta: ModelMeta) -> pd.DataFrame:
    """Takes features DataFrame and returns model predictions."""

    missing_ids = [col for col in REQUIRED_ID_COLUMNS if col not in features.columns]

    if missing_ids:
        raise ValueError(f'Feature table is missing column(s): {missing_ids}')

    missing_features = set(meta.feature_columns) - set(features.columns)

    if missing_features:
        raise ValueError(f'Feature table is missing feature(s): {missing_features}')

    # Build feature dataframe
    X = features[meta.feature_columns]

    for col, categories in meta.category_maps.items():
        X[col] = pd.Categorical(X[col], categories=categories)

    yhat = model.predict(X)

    df = features[REQUIRED_ID_COLUMNS].copy()
    df['target'] = meta.target
    df['predicted_value'] = yhat
    df['model_name'] = meta.model_name
    df['model_version'] = meta.model_version

    return df