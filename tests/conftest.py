import pathlib
import shutil

import pytest

from pathlibutil import Path


@pytest.fixture(scope='function')
def cls() -> Path:
    """return the same class for all test function"""

    hash = Path.default_hash
    yield Path
    Path.default_hash = hash


@pytest.fixture(scope='function')
def file(cls) -> Path:
    """new instance of Path for each test-function"""
    return cls(__file__)


@pytest.fixture
def tmp_dirpath(file: Path, cls: Path, tmp_path: pathlib.Path):

    shutil.copy(file, tmp_path)

    yield cls(tmp_path)


@pytest.fixture
def tmp_file(file: Path, tmp_dirpath: Path):

    yield tmp_dirpath.joinpath(file.name)
