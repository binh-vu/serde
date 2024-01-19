import bz2
import gzip
import os
from contextlib import contextmanager
from pathlib import Path
from typing import (
    Any,
    Generator,
    Iterable,
    Literal,
    Optional,
    Protocol,
    TypeVar,
    Union,
)

import chardet
import orjson
import zstandard as zstd
from typing_extensions import Self

try:
    import lz4.frame as lz4_frame  # type: ignore
except ImportError:
    lz4_frame = None

PathLike = Union[str, Path]
T = TypeVar("T")
DEFAULT_ORJSON_OPTS = orjson.OPT_NON_STR_KEYS

AVAILABLE_COMPRESSIONS = Literal["bz2", "gz", "lz4", "zstd"]


def get_open_fn(infile: PathLike, compression_level: Optional[int] = None) -> Any:
    """Get the correct open function for the input file based on its extension. Supported formats defined in the `AVAILABLE_COMPRESSIONS` variable.

    Parameters
    ----------
    infile : PathLike
        the file we wish to open
    compression_level : Optional[int], optional
        the compression level, by default None to use default compression
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
    elif infile.endswith(".zst"):
        if compression_level is None and "SERDE_ZSTD_COMPRESSION_LEVEL" in os.environ:
            compression_level = int(os.environ["SERDE_ZSTD_COMPRESSION_LEVEL"])

        default_compression_level = compression_level or 3

        @contextmanager
        def zstd_open(
            filepath: Path,
            mode: Literal["rb", "wb"],
            compression_level: Optional[int] = None,
        ):
            if compression_level is None:
                compression_level = default_compression_level

            compressor = zstd.ZstdCompressor(level=compression_level)
            if mode.find("r") != -1:
                with open(filepath, mode) as f:
                    yield compressor.stream_reader(f)
            else:
                with open(filepath, mode) as f:
                    yield compressor.stream_writer(f)

        return zstd_open
    else:
        return open


def get_compression(file: Union[str, Path]) -> Optional[AVAILABLE_COMPRESSIONS]:
    file = str(file)
    if file.endswith(".bz2"):
        return "bz2"
    if file.endswith(".gz"):
        return "gz"
    if file.endswith(".lz4"):
        return "lz4"
    if file.endswith(".zst"):
        return "zstd"
    return None


def get_filepath(
    file: Union[str, Path], compression: Optional[AVAILABLE_COMPRESSIONS]
) -> Path:
    if compression is None:
        return Path(file)
    if compression == "zstd":
        return Path(str(file) + ".zst")
    return Path(str(file) + f".{compression}")


def fix_encoding(fpath: Union[str, Path], backup_file: bool = True) -> Union[str, bool]:
    """Try to decode the context of the file as text in UTF-8, if it fails, try windows encoding before try to detect
    encoding of the file.

    If the encoding is not UTF-8,this function replace the content of the file with UTF-8 content and keep the backup
    if required.

    The function return True if the content is in UTF-8
    """
    with get_open_fn(str(fpath))(str(fpath), "rb") as f:
        content = f.read()

    try:
        content = content.decode("utf-8")
        return True
    except UnicodeDecodeError:
        pass

    try:
        content = content.decode("windows-1252")
    except UnicodeDecodeError:
        encoding = chardet.detect(content)["encoding"]
        content = content.decode(encoding)

    with get_open_fn(str(fpath))(str(fpath), "wb") as f:
        f.write(content.encode())

    return content


def iter_n(it: Iterable[T], n: int) -> Generator[T, None, None]:
    for value in it:
        yield value
        n -= 1
        if n == 0:
            break


def orjson_dumps(obj, **kwargs):
    if "default" not in kwargs:
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
