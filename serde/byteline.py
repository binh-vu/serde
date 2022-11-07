from __future__ import annotations

from collections.abc import Sequence

from serde.helper import PathLike, get_open_fn


def deser(
    fpath: PathLike, n_lines: int | None = None, trim: bool = False
) -> list[bytes]:
    """Deserialize byte lines, each line should never have byte b'\n'."""
    with get_open_fn(fpath)(str(fpath), "rb") as f:
        if n_lines is None:
            return [line for line in f]
        lst = []
        for line in f:
            lst.append(line)
            if len(lst) >= n_lines:
                break
        return lst


def ser(objects: Sequence[bytes], fpath: PathLike):
    with get_open_fn(fpath)(str(fpath), "wb") as f:
        for obj in objects:
            f.write(obj)
            f.write(b"\n")
