from typing import Any
from ruamel.yaml import YAML
from serde.helper import PathLike, get_open_fn


def deser(file: PathLike):
    with get_open_fn(file)(str(file), "rb") as f:
        yaml = YAML()
        return yaml.load(f)


def ser(obj: Any, file: PathLike):
    with get_open_fn(file)(str(file), "wb") as f:
        yaml = YAML()
        yaml.dump(obj, f)
        
        