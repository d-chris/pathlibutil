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
