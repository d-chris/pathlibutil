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


def test_expand_files(prj_path):
    pattern = prj_path / "tests/test_*.py"

    files = list(Path.expand(pattern))

    assert len(files) > 0
    assert all(p.name.startswith("test_") for p in files)


def test_expand_missing():
    gen = Path.expand("missing*.txt", __file__)

    assert list(gen) == [Path(__file__)]


def test_expand_duplicates():

    files = [__file__] * 3

    gen = Path.expand(*files, duplicates=False)

    assert list(gen) == [Path(__file__)]
