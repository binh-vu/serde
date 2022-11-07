from __future__ import annotations

from collections.abc import Sequence

from serde.helper import PathLike, get_open_fn


def deser(fpath: PathLike, n_lines: int | None = None, trim: bool = False) -> list[str]:
    with get_open_fn(fpath)(str(fpath), "rb") as f:
        if n_lines is None:
            if trim:
                return [line.decode().strip() for line in f]
            return [line.decode() for line in f]

        lst = []
        if trim:
            for line in f:
                lst.append(line.decode().strip())
                if len(lst) >= n_lines:
                    break
        else:
            for line in f:
                lst.append(line.decode())
                if len(lst) >= n_lines:
                    break
        return lst


def ser(objects: Sequence[str], fpath: PathLike):
    with get_open_fn(fpath)(str(fpath), "wb") as f:
        for obj in objects:
            f.write(obj.encode())
            f.write(b"\n")
