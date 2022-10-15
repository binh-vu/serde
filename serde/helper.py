from typing import Generator, Iterable, Protocol, Union, TypeVar
from typing_extensions import Self
from pathlib import Path
import bz2
import gzip
import orjson

try:
    import lz4.frame as lz4_frame  # type: ignore
except ImportError:
    lz4_frame = None

PathLike = Union[str, Path]
T = TypeVar("T")
DEFAULT_ORJSON_OPTS = orjson.OPT_NON_STR_KEYS


def get_open_fn(infile: PathLike):
    """Get the correct open function for the input file based on its extension. Supported bzip2, gz

    Parameters
    ----------
    infile : PathLike
        the file we wish to open

    Returns
    -------
    Callable
        the open function that can use to open the file

    Raises
    ------
    ValueError
        when encounter unknown extension
    """
    infile = str(infile)

    if infile.endswith(".bz2"):
        return bz2.open
    elif infile.endswith(".gz"):
        return gzip.open
    elif infile.endswith(".lz4"):
        if lz4_frame is None:
            raise ValueError("lz4 is not installed")
        return lz4_frame.open
    else:
        return open


def iter_n(it: Iterable[T], n: int) -> Generator[T, None, None]:
    for value in it:
        yield value
        n -= 1
        if n == 0:
            break


def orjson_dumps(obj, **kwargs):
    if kwargs.get('default', None) is None:
        return orjson.dumps(obj, default=_orjson_default, **kwargs)
    return orjson.dumps(obj, **kwargs)


def _orjson_default(obj):
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


class JsonSerde(Protocol):
    def to_dict(self) -> dict:
        ...

    @classmethod
    def from_dict(cls, obj: dict) -> Self:
        ...