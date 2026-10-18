import os
from pathlib import Path

import pytest

from gitb.service.IOService import is_file_directory_writable, is_file_writable


def test_existing_file_is_not_truncated(tmp_path: Path) -> None:
    file = tmp_path / "keep.txt"
    file.write_text("data")
    assert is_file_writable(str(file))
    assert file.read_text() == "data"


def test_missing_file_is_not_created(tmp_path: Path) -> None:
    file = tmp_path / "new.json"
    assert is_file_writable(str(file))
    assert not file.exists()


def test_directory_is_not_a_writable_file(tmp_path: Path) -> None:
    assert not is_file_writable(str(tmp_path))


def test_relative_path_uses_current_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    assert is_file_directory_writable("out.json")
    assert is_file_writable("out.json")


@pytest.mark.skipif(os.geteuid() == 0, reason="root can write anywhere")
def test_read_only_directory(tmp_path: Path) -> None:
    tmp_path.chmod(0o500)
    try:
        assert not is_file_writable(str(tmp_path / "new.json"))
    finally:
        tmp_path.chmod(0o700)
