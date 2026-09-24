import pandas as pd
from sqlalchemy import create_engine, text

def load_predictions(db_url: str, schema: str, table: str, predictions: pd.DataFrame) -> None:
    """Loads predictions DataFrame to database."""

    engine = create_engine(db_url)

    model_name = predictions['model_name'].iloc[0]
    model_version = predictions['model_version'].iloc[0]
    target = predictions['target'].iloc[0]

    with engine.connect() as conn:
        conn.execute(
            text(f"""
                DELETE FROM {schema}.{table}
                WHERE model_name = :model_name
                AND model_version = :model_version
                AND target = :target
            """),
            {'model_name': model_name, 'model_version': model_version, 'target': target}
        )

        predictions.to_sql(f'{schema}.{table}', conn, if_exists='append', index=False)