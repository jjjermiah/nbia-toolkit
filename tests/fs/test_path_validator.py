import os

import pytest

from nbiatoolkit.fs import PathValidator


def test_non_existent_path(tmp_path):
    validator = PathValidator("path", exists=True)
    non_existent_path = tmp_path / "non_existent"
    with pytest.raises(FileNotFoundError):
        validator.validate("path", non_existent_path)


def test_directory_validation(tmp_path):
    validator = PathValidator("path", dir_okay=False)
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()
    with pytest.raises(IsADirectoryError):
        validator.validate("path", dir_path)
    dir_path.rmdir()


def test_file_validation(tmp_path):
    validator = PathValidator("path", file_okay=False)
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test")
    with pytest.raises(ValueError):
        validator.validate("path", file_path)
    file_path.unlink()


def test_allowed_extensions(tmp_path):
    validator = PathValidator("path", file_okay=True, allowed_extensions=[".txt"])
    file_path = tmp_path / "test_file.csv"
    file_path.write_text("test")
    with pytest.raises(ValueError):
        validator.validate("path", file_path)
    file_path.unlink()


def test_readability(tmp_path):
    validator = PathValidator("path", readable=True)
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test")
    os.chmod(file_path, 0o000)
    with pytest.raises(PermissionError):
        validator.validate("path", file_path)
    os.chmod(file_path, 0o644)  # Change permissions back to delete the file
    file_path.unlink()


def test_writability(tmp_path):
    validator = PathValidator("path", writable=True)
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test")
    os.chmod(file_path, 0o444)
    with pytest.raises(PermissionError):
        validator.validate("path", file_path)
    os.chmod(file_path, 0o644)  # Change permissions back to delete the file
    file_path.unlink()


def test_executability(tmp_path):
    validator = PathValidator("path", executable=True)
    file_path = tmp_path / "test_file.sh"
    file_path.write_text("test")
    os.chmod(file_path, 0o644)
    with pytest.raises(PermissionError):
        validator.validate("path", file_path)
    file_path.unlink()


def test_mkdirs(tmp_path):
    validator = PathValidator("path", dir_okay=True, mkdirs=True)
    new_dir_path = tmp_path / "new_dir"
    validator.validate("path", new_dir_path)
    assert new_dir_path.exists() and new_dir_path.is_dir()
