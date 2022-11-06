import csv
from typing import List
from serde.helper import PathLike, get_open_fn


def deser(file: PathLike, delimiter: str = ","):
    with get_open_fn(file)(str(file), "r") as f:
        reader = csv.reader(f, delimiter=delimiter)
        return [row for row in reader]


def ser(rows: List[List[str]], file: PathLike, mode: str = "w", delimiter: str = ","):
    with get_open_fn(file)(str(file), mode, newline="") as f:
        writer = csv.writer(
            f, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL, lineterminator="\n"
        )
        for row in rows:
            writer.writerow(row)
