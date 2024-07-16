import random

import exrex
import pytest

from pathlibutil import Path
from pathlibutil.types import ByteInt, byteint


@pytest.fixture(
    params=[
        (1e3, "kb", 1),
        (1e6, "mb", 1),
        (1e9, "gb", 1),
        (1e12, "tb", 1),
        (1e15, "pb", 1),
        (1e18, "eb", 1),
        (1e21, "zb", 1),
        (1e24, "yb", 1),
        (2**10, "kib", 1),
        (2**20, "mib", 1),
        (2**30, "gib", 1),
        (2**40, "tib", 1),
        (2**50, "pib", 1),
        (2**60, "eib", 1),
        (2**70, "zib", 1),
        (2**80, "yib", 1),
    ]
)
def params(request):
    """returns a tuple of byte, unit and result"""
    return request.param


@pytest.fixture(
    params=[
        (0, "0 b"),
        (1, "1 b"),
        (12, "12 b"),
        (123, "123 b"),
        (1234, "1.23 kb"),
        (12345, "12.35 kb"),
        (123456, "123.5 kb"),
        (1234567, "1.23 mb"),
    ]
)
def decimal(request):
    """returns a tuple of random int and its decimal string representation"""
    return request.param


@pytest.fixture(
    params=[
        (0, "0 b"),
        (1, "1 b"),
        (12, "12 b"),
        (123, "123 b"),
        (1234, "1.21 kib"),
        (12345, "12.06 kib"),
        (123456, "120.6 kib"),
        (1234567, "1.18 mib"),
    ]
)
def binary(request):
    """returns a tuple of random int and its binary string representation"""
    return request.param


@pytest.fixture(params=exrex.generate(r"[zyeptgmk]i?b"))
def unit(request):
    """generate units from regex, eg. kb, kib, mb, mib, ..."""
    return request.param


def test_class():
    assert issubclass(ByteInt, int)


def test_attributes(params):
    value, unit, result = params

    factor = random.randint(1, 1000)

    assert getattr(ByteInt(factor * value), unit) == pytest.approx(factor * result)


def test_attribute_raises():
    with pytest.raises(AttributeError):
        ByteInt(1).bb

    with pytest.raises(AttributeError):
        ByteInt(1).bib


def test_format():
    b = ByteInt(1)

    assert f"{b:d}" == "1"
    assert f"{b:.0f}" == "1"

    with pytest.raises(ValueError):
        f"{b:KB}" == "0.001"


def test_format_params(params):
    value, unit, _ = params

    result = random.randint(1, 1000)

    assert ByteInt(value * result).__format__(f".1{unit}") == f"{result:.1f}"


def test_size():
    """check if size return ByteInt from file and directory"""

    p = Path(__file__)

    assert type(p.size()) is ByteInt
    assert type(p.parent.size()) is ByteInt


def test_unit(unit):
    """check if unit is in ByteInt.units"""

    assert unit in ByteInt().units


def test_info(unit):
    """generate units from regex and check if info returns correct types"""

    b, u = ByteInt.info(unit)

    assert type(b) is int
    assert b >= 1000
    assert type(u) is str


@pytest.mark.parametrize(
    "func",
    [
        "__add__",
        "__sub__",
        "__mul__",
        "__floordiv__",
        "__mod__",
        "__iadd__",
        "__isub__",
        "__imul__",
        "__ifloordiv__",
        "__imod__",
    ],
)
def test_operations(func):
    """check if result is a ByteInt object of operation functions"""

    b = ByteInt(2)

    operation = getattr(b, func)

    assert type(operation(1)) is ByteInt


def test_decorator():
    randbyte = byteint(random.randint)

    assert type(randbyte(0, 2**64)) is ByteInt

    @byteint
    def randhexbyte():
        return hex(random.randint(0, 2**32))

    assert type(randhexbyte()) is str


def test_string(decimal):
    """check decimal str() representation"""

    arg, result = decimal
    assert str(ByteInt(arg)) == result


def test_string_decimal(decimal):
    """check decimal string reprensentation"""

    arg, result = decimal
    assert ByteInt(arg).string() == result


def test_string_binary(binary):
    """check binary string reprensentation"""

    arg, result = binary
    assert ByteInt(arg).string(False) == result
