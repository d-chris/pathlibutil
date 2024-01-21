import random

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
    p = Path(__file__)

    assert type(p.size()) is ByteInt
    assert type(p.parent.size()) is ByteInt


def test_unit_info():
    assert hasattr(ByteInt, "info")
    assert hasattr(ByteInt, "units")

    for unit in ByteInt().units:
        assert type(unit) is str

        byte, name = ByteInt.info(unit)

        assert type(byte) is int
        assert byte >= 1000
        assert type(name) is str


def test_inplaceoperation():
    a = ByteInt(1)

    a += 1
    assert type(a) is ByteInt

    a -= 1
    assert type(a) is ByteInt

    a *= 2
    assert type(a) is ByteInt

    a //= 2
    assert type(a) is ByteInt

    a %= 1
    assert type(a) is ByteInt


def test_operation():
    a = ByteInt(1)

    c = a + 1
    assert type(c) is ByteInt

    c = a - 1
    assert type(c) is ByteInt

    c = a * 2
    assert type(c) is ByteInt

    c = a // 2
    assert type(c) is ByteInt

    c = a % 1
    assert type(c) is ByteInt


def test_decorator():
    randbyte = byteint(random.randint)

    assert type(randbyte(0, 2**64)) is ByteInt

    @byteint
    def randhexbyte():
        return hex(random.randint(0, 2**32))

    assert type(randhexbyte()) is str


def test_string():
    assert str(ByteInt(1)) == "1 b"
    assert str(ByteInt(1234)) == "1.23 kb"
    assert str(ByteInt(12345)) == "12.35 kb"
    assert str(ByteInt(123456)) == "123.5 kb"

    assert ByteInt(12345).string(False) == "12.06 kib"
    assert ByteInt(123456).string(False) == "120.6 kib"
