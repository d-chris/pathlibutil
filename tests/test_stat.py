import os

import pytest

from pathlibutil.path import Path
from pathlibutil.types import ByteInt, StatResult, TimeInt


def test_stat():
    """check if stat() returns wrapper object StatResult"""

    s = Path(__file__).stat()

    assert type(s) == StatResult


@pytest.mark.parametrize("arg", [a for a in dir(os.stat_result) if a.startswith("__")])
def test_stat_attr(arg):
    """check if the wrapper has all attributes of os.stat_result"""

    s = Path(__file__).stat()

    assert getattr(s, arg) is not None


@pytest.mark.parametrize(
    "arg", [a for a in dir(os.stat_result) if not a.startswith("__")]
)
def test_stat_attr_result(arg):
    """check if the wrapper has all attributes of os.stat_result"""

    s = Path(__file__).stat()
    o = os.stat(__file__)

    attr = getattr(o, arg)

    if not callable(attr):
        assert getattr(s, arg) == attr
    else:
        pytest.skip(f"{arg} is callable and not tested")


@pytest.mark.parametrize("time", [t for t in dir(os.stat_result) if t.endswith("time")])
def test_stat_time(time):
    """check if the results for times are TimeInt objects"""

    s = Path(__file__).stat()

    assert type(getattr(s, time)) == TimeInt


def test_stat_size():
    """check if the result for st_size is a ByteInt object"""

    s = Path(__file__).stat()

    assert type(s.st_size) == ByteInt


@pytest.mark.parametrize("cast", [str, repr, dir, len])
def test_stat_functions(cast):
    s = Path(__file__).stat()
    o = os.stat(__file__)

    assert cast(s) == cast(o)


def test_stat_result():
    """check if the result for st_result is a StatResult object"""

    s = Path(__file__).stat()

    assert type(s.stat_result) == os.stat_result
