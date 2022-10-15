import orjson
from typing import Any, Callable, Optional, Union, Type
from serde.helper import DEFAULT_ORJSON_OPTS, JsonSerde, PathLike, get_open_fn, orjson_dumps


def deser(file: PathLike, cls: Optional[Type[JsonSerde]] = None):
    with get_open_fn(file)(str(file), "rb") as f:
        if cls is not None:
            return cls.from_dict(orjson.loads(f.read()))
        return orjson.loads(f.read())


def ser(obj: Union[tuple, list, dict, JsonSerde], file: PathLike, orjson_opts: Optional[int] = DEFAULT_ORJSON_OPTS, orjson_default: Optional[Callable[[Any], Any]] = None):
    with get_open_fn(file)(str(file), "wb") as f:
        if hasattr(obj, "to_dict"):
            f.write(orjson_dumps(obj.to_dict(), option=orjson_opts, default=orjson_default))  # type: ignore
        else:
            f.write(orjson_dumps(obj, option=orjson_opts, default=orjson_default))
        
        