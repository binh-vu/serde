import pickle
from typing import Any
from serde.helper import PathLike, get_open_fn


def deser(file: PathLike):
    with get_open_fn(file)(str(file), "rb") as f:
        return pickle.load(f)


def ser(obj: Any, file: PathLike):
    with get_open_fn(file)(str(file), "wb") as f:
        pickle.dump(obj, f)
