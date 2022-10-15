import orjson
from typing import Any, Optional, Union, Type, List, Callable
from serde.helper import DEFAULT_ORJSON_OPTS, JsonSerde, PathLike, get_open_fn, iter_n, orjson_dumps


def deser(file: PathLike, nlines: Optional[int] = None, cls: Optional[Type[JsonSerde]] = None):
    with get_open_fn(file)(str(file), "rb") as f:
        if nlines is None:
            it = f
        else:
            it = iter_n(f, nlines)
        
        if cls is not None:
            return [cls.from_dict(orjson.loads(line)) for line in it]
        return [orjson.loads(line) for line in it]


def ser(objs: Union[List[dict], List[tuple], List[list], List[JsonSerde]], file: PathLike, orjson_opts: Optional[int] = DEFAULT_ORJSON_OPTS, orjson_default: Optional[Callable[[Any], Any]] = None):
    with get_open_fn(file)(str(file), "wb") as f:
        if len(objs) > 0 and hasattr(objs[0], "to_dict"):
            for obj in objs:
                f.write(orjson_dumps(obj.to_dict(), option=orjson_opts, default=orjson_default))  # type: ignore
                f.write(b"\n")
        else:
            for obj in objs:
                f.write(orjson_dumps(obj, option=orjson_opts, default=orjson_default))
                f.write(b"\n")
        
        