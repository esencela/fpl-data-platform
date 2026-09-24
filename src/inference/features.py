import pandas as pd
from sqlalchemy import create_engine, text

def get_prediction_features(db_url: str, schema: str, table: str) -> pd.DataFrame:
    """Reads prediction features from database and returns a pandas DataFrame."""

    engine = create_engine(db_url)

    query = text(f'SELECT * FROM {schema}.{table}')

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    if df.empty():
        raise ValueError(f'No feature rows found in {schema}.{table}')

    return df