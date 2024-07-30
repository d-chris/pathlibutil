import datetime
import random

import pytest

from pathlibutil.types import TimeInt


@pytest.fixture
def timeint():
    fmt = TimeInt.format

    yield TimeInt(0, datetime.timezone.utc)

    TimeInt.format = fmt


@pytest.mark.parametrize("cast", [int, float, str])
def test_timeint(cast):
    """check that TimeInt can work with int, float and str"""

    arg = cast(random.uniform(0, 2**32))

    t = TimeInt(arg)
    assert type(t) is TimeInt


def test_epoch():
    """check TimeInt(0) returns the epoch, if tz is None the local timezone is used"""

    tz = datetime.timezone.utc
    t = TimeInt(0, tz)

    assert t.datetime == datetime.datetime(1970, 1, 1, 0, 0, tzinfo=tz)


def test_string(timeint):
    """check string representation of TimeInt"""

    assert timeint.string("pytest:%d.%m.%Y") == "pytest:01.01.1970"
    assert str(timeint) == "1970-01-01 00:00:00"


def test_format(timeint):
    """check class attribute TimeInt.format"""

    assert str(timeint) == "1970-01-01 00:00:00"

    TimeInt.format = "%H:%M Uhr %d.%m.%Y"

    assert str(timeint) == "00:00 Uhr 01.01.1970"
