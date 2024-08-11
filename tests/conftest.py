import pathlib
import shutil
from typing import Any, Generator
from unittest.mock import Mock

import pytest

from pathlibutil import Path


@pytest.fixture
def cls() -> Generator[Path, Any, Any]:
    """return the same class for all test function"""

    hash = Path.default_hash
    yield Path
    Path.default_hash = hash


@pytest.fixture
def file(cls) -> Path:
    """new instance of Path for each test-function"""
    return cls(__file__)


@pytest.fixture
def prj_path() -> pathlib.Path:
    """return the root path of the project"""

    return pathlib.Path(__file__).joinpath("../../")


@pytest.fixture
def mocked_cls(mocker):

    # Use mocker to patch hashlib.new
    mock_hashlib_new = mocker.patch("hashlib.new")
    mock = Mock()
    mock.hexdigest.return_value = "0123456789abcdef"
    mock_hashlib_new.return_value = mock

    hash = Path.default_hash
    yield Path
    Path.default_hash = hash


@pytest.fixture
def mocked_file(mocked_cls) -> Path:
    return mocked_cls(__file__)


@pytest.fixture
def tmp_dirpath(file: Path, cls: Path, tmp_path: pathlib.Path):
    shutil.copy(file, tmp_path)

    yield cls(tmp_path)


@pytest.fixture
def tmp_file(file: Path, tmp_dirpath: Path):
    yield tmp_dirpath.joinpath(file.name)
