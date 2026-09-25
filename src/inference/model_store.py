import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

@dataclass
class ModelMeta:
    model_name: str
    model_version: str
    target: str
    feature_columns: list[str]
    categorical_columns: list[str]
    category_maps: dict
    trained_through_season: int
    trained_at: str
    framework: str
    framework_version: str


class ModelStore(Protocol):
    def load(self, model_dir: str) -> tuple[Any, ModelMeta]:
        ...


class LocalModelStore:
    def __init__(self, model_dir: str):
        self.model_dir = model_dir

    def load(self) -> tuple[Any, ModelMeta]:
        """Loads a model and its metadata from the local filesystem."""
        model_path = Path(self.model_dir) / 'model.pkl'
        meta_path = Path(self.model_dir) / 'meta.json'

        if not model_path.exists():
            raise FileNotFoundError(f'Model not found in {self.model_dir}')

        if not meta_path.exists():
            raise FileNotFoundError(f'Metadata not found in {self.model_dir}')

        with open(meta_path, 'r', encoding='utf-8') as file:
            raw = json.load(file)
            meta = ModelMeta(
                model_name=raw['model_name'],
                model_version=raw['model_version'],
                target=raw['target'],
                feature_columns=raw['feature_columns'],
                categorical_columns=raw['categorical_columns'],
                category_maps=raw['category_maps'],
                trained_through_season=raw['trained_through_season'],
                trained_at=raw['trained_at'],
                framework=raw['framework'],
                framework_version=raw['framework_version']
            )

        with open(model_path, 'rb') as file:
            model = pickle.load(file)

        return model, meta