from inspect import isgenerator

import pytest

from pathlibutil import Path


def test_expand_generator():
    gen = Path.expand(__file__)

    assert isgenerator(gen)


def test_expand():
    gen = Path.expand(__file__)

    assert list(gen) == [Path(__file__)]


def test_expand_raises():

    with pytest.raises(TypeError):
        list(Path.expand(None))


def test_expand_files():
    gen = Path.expand("tests/test_*.py")
    files = list(gen)

    assert len(files) > 1
    assert all(p.name.startswith("test_") for p in files)


def test_expand_missing():
    gen = Path.expand("missing*.txt", __file__)

    assert list(gen) == [Path(__file__)]
