import shutil
from pathlib import Path

import pytest

from serde.helper import get_open_fn


@pytest.mark.parametrize("format", ["bz2", "gz", "lz4", "zst"])
def test_open_fn_context(format, tmpdir):
    # compress and decompress the data should be the same
    testfile = Path(tmpdir) / f"test.txt.{format}"
    testfile2 = Path(tmpdir) / f"test_copied.txt.{format}"

    data = b"line1\nline2"
    with get_open_fn(testfile)(testfile, "wb") as f:
        f.write(data)

    compressed_data = testfile.read_bytes()
    assert compressed_data != data and len(compressed_data) > 0

    shutil.copy(testfile, testfile2)

    with get_open_fn(testfile2)(testfile2, "rb") as f:
        decompressed_data = f.read()

    assert decompressed_data == data

    with get_open_fn(testfile2)(testfile2, "rb") as f:
        assert f.readline() == b"line1\n"
        assert f.readline() == b"line2"


@pytest.mark.parametrize("format", ["bz2", "gz", "lz4", "zst"])
def test_open_fn(format, tmpdir):
    # compress and decompress the data should be the same
    testfile = Path(tmpdir) / f"test.txt.{format}"
    testfile2 = Path(tmpdir) / f"test_copied.txt.{format}"

    data = b"line1\nline2\n"
    file = get_open_fn(testfile)(testfile, "wb")
    file.write(data)
    file.close()

    compressed_data = testfile.read_bytes()
    assert compressed_data != data and len(compressed_data) > 0

    shutil.copy(testfile, testfile2)

    file = get_open_fn(testfile2)(testfile2, "rb")
    decompressed_data = file.read()
    file.close()

    assert decompressed_data == data

    with get_open_fn(testfile2)(testfile2, "rb") as f:
        assert f.readline() == b"line1\n"
        assert f.readline() == b"line2\n"
        assert f.readline() == b""
