import shutil
from pathlib import Path

import pytest
import zstandard as zstd

from serde.helper import get_open_fn


@pytest.mark.parametrize("format", ["bz2", "gz", "lz4", "zst"])
def test_open_fn(format, tmpdir):
    # compress and decompress the data should be the same
    testfile = Path(tmpdir) / f"test.txt.{format}"
    testfile2 = Path(tmpdir) / f"test_copied.txt.{format}"

    data = b'{"msg": "hello world"}'
    with get_open_fn(testfile)(testfile, "wb") as f:
        f.write(data)

    compressed_data = testfile.read_bytes()
    assert compressed_data != data and len(compressed_data) > 0

    shutil.copy(testfile, testfile2)

    with get_open_fn(testfile2)(testfile2, "rb") as f:
        decompressed_data = f.read()

    assert decompressed_data == data
