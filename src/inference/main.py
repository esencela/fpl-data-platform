from config.settings import settings
from inference.model_store import LocalModelStore
from inference.features import get_prediction_features
from inference.predict import predict
from inference.load import load_predictions

def main():
    db_url = f"postgresql://{settings.postgres_user}:{settings.postgres_password}"\
            f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

    model, meta = LocalModelStore(settings.MODEL_DIR).load()
    features = get_prediction_features(db_url, settings.ML_SCHEMA, settings.FEATURES_TABLE)
    predictions = predict(features, model, meta)
    load_predictions(db_url, settings.ML_SCHEMA, settings.PREDICTION_TABLE, predictions)


if __name__ == '__main__':
    main()