from __future__ import annotations

import csv
from io import StringIO
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Union,
    overload,
)

from serde.helper import PathLike, get_open_fn


@overload
def deser(
    file: Union[PathLike, StringIO],
    delimiter: str = ",",
    deser_as_record: Literal[False] = False,
    dtype: Optional[dict[Union[str, int], Callable[[str], Any]]] = None,
) -> List[List[str]]: ...


@overload
def deser(
    file: Union[PathLike, StringIO],
    delimiter: str = ",",
    deser_as_record: Literal[True] = True,
    dtype: Optional[dict[Union[str, int], Callable[[str], Any]]] = None,
) -> List[Dict[str, Any]]: ...


def deser(
    file: Union[PathLike, StringIO],
    delimiter: str = ",",
    deser_as_record: bool = False,
    dtype: Optional[Mapping[Union[str, int], Callable[[str], Any]]] = None,
) -> Union[List[List[str]], List[Dict[str, Any]]]:
    """Deserialize a csv record

    Args:
        file (PathLike): file path
        delimiter (str, optional): delimiter. Defaults to ",".
        deser_as_record (bool, optional): deserialize as list of records/dictionaries. Defaults to False.
        dtype (Optional[dict[Union[str, int], Callable[[str], Any]]], optional): data type. Defaults to None.
    """
    if isinstance(file, StringIO):
        reader = csv.reader(file, delimiter=delimiter)

        if deser_as_record:
            it = iter(reader)
            try:
                header = next(it)
            except StopIteration:
                return []

            if dtype is None:
                return [dict(zip(header, row)) for row in it]

            # convert dtype to a list of index
            norm_fns = []
            for ci, fn in dtype.items():
                if isinstance(ci, str):
                    ci = header.index(ci)
                elif ci < 0:
                    ci = len(header) + ci
                if fn is bool:
                    fn = lambda x: bool(int(x))
                norm_fns.append((ci, fn))

            output = []
            for row in it:
                for ci, fn in norm_fns:
                    row[ci] = fn(row[ci])
                output.append(dict(zip(header, row)))
            return output

        return [row for row in reader]

    with get_open_fn(file)(str(file), mode="r") as f:
        reader = csv.reader(f, delimiter=delimiter)

        if deser_as_record:
            it = iter(reader)
            try:
                header = next(it)
            except StopIteration:
                return []

            if dtype is None:
                return [dict(zip(header, row)) for row in it]

            # convert dtype to a list of index
            norm_fns = []
            for ci, fn in dtype.items():
                if isinstance(ci, str):
                    ci = header.index(ci)
                elif ci < 0:
                    ci = len(header) + ci
                if fn is bool:
                    fn = lambda x: bool(int(x))
                norm_fns.append((ci, fn))

            output = []
            for row in it:
                for ci, fn in norm_fns:
                    row[ci] = fn(row[ci])
                output.append(dict(zip(header, row)))
            return output

        return [row for row in reader]


def ser(
    rows: Sequence[Union[Mapping[str, str | bool | int | float], Sequence[str]]],
    file: Union[PathLike, StringIO],
    mode: str = "wt",
    delimiter: str = ",",
):
    if isinstance(file, StringIO):
        writer = csv.writer(
            file, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL, lineterminator="\n"
        )

        if len(rows) > 0 and isinstance(rows[0], Mapping):
            header = list(rows[0].keys())
            writer.writerow(header)

            bool_headers = [
                i for i, h in enumerate(header) if isinstance(rows[0][h], bool)
            ]
            if len(bool_headers) == 0:
                for row in rows:
                    writer.writerow((row[h] for h in header))  # type: ignore
            else:
                for row in rows:
                    tmp = [row[h] for h in header]  # type: ignore
                    for i in bool_headers:
                        tmp[i] = int(tmp[i])
                    writer.writerow(tmp)
        else:
            for row in rows:
                writer.writerow(row)
    else:
        # mode = wt as gzip does not support newline in binary mode
        with get_open_fn(file)(str(file), mode, newline="") as f:
            writer = csv.writer(
                f, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL, lineterminator="\n"
            )

            if len(rows) > 0 and isinstance(rows[0], Mapping):
                header = list(rows[0].keys())
                writer.writerow(header)

                bool_headers = [
                    i for i, h in enumerate(header) if isinstance(rows[0][h], bool)
                ]
                if len(bool_headers) == 0:
                    for row in rows:
                        writer.writerow((row[h] for h in header))  # type: ignore
                else:
                    for row in rows:
                        tmp = [row[h] for h in header]  # type: ignore
                        for i in bool_headers:
                            tmp[i] = "true" if tmp[i] else "false"
                        writer.writerow(tmp)
            else:
                for row in rows:
                    writer.writerow(row)
