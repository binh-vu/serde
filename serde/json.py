from typing import Any, Callable, Literal, Optional, Type, TypeVar, Union, overload

import orjson

from serde.helper import (
    DEFAULT_ORJSON_OPTS,
    JsonSerde,
    PathLike,
    get_open_fn,
    orjson_dumps,
)

T = TypeVar("T", bound=JsonSerde)


@overload
def deser(file: PathLike, cls: Type[T]) -> T: ...


@overload
def deser(file: PathLike) -> Any: ...


def deser(file: PathLike, cls: Optional[Type[T]] = None) -> Union[Any, T]:
    with get_open_fn(file)(str(file), "rb") as f:
        if cls is not None:
            return cls.from_dict(orjson.loads(f.read()))
        return orjson.loads(f.read())


def ser(
    obj: Union[tuple, list, dict, JsonSerde],
    file: PathLike,
    indent: Literal[0, 2] = 0,
    orjson_opts: Optional[int] = DEFAULT_ORJSON_OPTS,
    orjson_default: Optional[Callable[[Any], Any]] = None,
):
    if indent > 0:
        orjson_opts = (
            orjson_opts | orjson.OPT_INDENT_2
            if orjson_opts is not None
            else orjson.OPT_INDENT_2
        )

    if hasattr(obj, "to_dict"):
        data = orjson_dumps(obj.to_dict(), option=orjson_opts, default=orjson_default)  # type: ignore
    else:
        data = orjson_dumps(obj, option=orjson_opts, default=orjson_default)

    with get_open_fn(file)(str(file), "wb") as f:
        f.write(data)
