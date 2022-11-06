from __future__ import annotations

import orjson
from typing import (
    Any,
    TypeVar,
    Type,
    Callable,
    overload,
)
from collections.abc import Sequence
from serde.helper import (
    DEFAULT_ORJSON_OPTS,
    JsonSerde,
    PathLike,
    _orjson_default,
    get_open_fn,
    iter_n,
    orjson_dumps,
)

T = TypeVar("T", bound=JsonSerde)


@overload
def deser(file: PathLike, nlines: int | None = None, cls: Type[T] = None) -> list[T]:
    ...


@overload
def deser(file: PathLike, nlines: int | None = None) -> list:
    ...


def deser(
    file: PathLike, nlines: int | None = None, cls: Type[JsonSerde] | None = None
):
    with get_open_fn(file)(str(file), "rb") as f:
        if nlines is None:
            it = f
        else:
            it = iter_n(f, nlines)

        if cls is not None:
            return [cls.from_dict(orjson.loads(line)) for line in it]
        return [orjson.loads(line) for line in it]


def ser(
    objs: Sequence[dict] | Sequence[tuple] | Sequence[list] | Sequence[JsonSerde],
    file: PathLike,
    orjson_opts: int | None = DEFAULT_ORJSON_OPTS,
    orjson_default: Callable[[Any], Any] | None = None,
):
    with get_open_fn(file)(str(file), "wb") as f:
        if len(objs) > 0 and hasattr(objs[0], "to_dict"):
            for obj in objs:
                f.write(
                    orjson_dumps(
                        obj.to_dict(),  # type: ignore
                        option=orjson_opts,
                        default=orjson_default or _orjson_default,
                    )
                )
                f.write(b"\n")
        else:
            for obj in objs:
                f.write(
                    orjson_dumps(
                        obj,
                        option=orjson_opts,
                        default=orjson_default or _orjson_default,
                    )
                )
                f.write(b"\n")
