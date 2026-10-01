import json
import pickle
import pytest
from inference.model_store import LocalModelStore, ModelMeta

TEST_MODEL = {"model_name": "test_model"}


def metadata():
    # Returns a sample metadata dictionary for testing purposes.
    return {
        "model_name": "test_model",
        "model_version": "1.0",
        "target": "target_variable",
        "feature_columns": ["feature1", "feature2"],
        "categorical_columns": ["feature1"],
        "category_maps": {"feature1": ["A", "B", "C"]},
        "trained_through_season": 2023,
        "trained_at": "2023-01-01T00:00:00Z",
        "framework": "lightgbm",
        "framework_version": "3.3.2"
    }


def write_metadata(model_dir, meta: dict) -> None:
    """Writes test metadata dict to JSON file in specified model directory."""
    meta_path = model_dir / 'meta.json'
    meta_path.write_text(json.dumps(meta), encoding='utf-8')


@pytest.fixture
def model_dir(tmp_path):
    """Creates a temporary directory with a test model and metadata for testing."""
    model_dir = tmp_path / 'test_model'
    model_dir.mkdir(parents=True, exist_ok=True)

    write_metadata(model_dir, metadata())

    model_path = model_dir / 'model.pkl'
    model_path.write_bytes(pickle.dumps(TEST_MODEL))

    return model_dir


def test_local_model_store_load_success(model_dir):
    model, meta = LocalModelStore(str(model_dir)).load()

    assert model == TEST_MODEL
    assert meta == ModelMeta(**metadata())


def test_local_model_store_load_missing_model(model_dir):
    # Remove model file
    (model_dir / 'model.pkl').unlink()

    with pytest.raises(FileNotFoundError, match='Model not found'):
        LocalModelStore(str(model_dir)).load()


def test_local_model_store_load_missing_metadata(model_dir):
    # Remove metadata file
    (model_dir / 'meta.json').unlink()

    with pytest.raises(FileNotFoundError, match='Metadata not found'):
        LocalModelStore(str(model_dir)).load()