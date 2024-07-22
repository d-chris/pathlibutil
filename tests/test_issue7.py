import pathlib
from typing import Any

import pytest

from pathlibutil import Path, Register7zFormat


class DummyPath(Register7zFormat):
    """
    pathlib.Path > pathlibutil.Path > Register7zFormat > DummyPath
    """

    pass


@pytest.fixture(
    params=[Path, Register7zFormat, DummyPath],
    ids=lambda params: params.__name__,
)
def cls(request: pytest.FixtureRequest):
    return request.param


def test_subclass(cls: Any):
    assert isinstance(cls(__file__), pathlib.Path)
    assert issubclass(cls, pathlib.Path)


def test_copy_type(tmp_path: pathlib.Path, cls: Any):
    p = cls(__file__).copy(tmp_path)
    assert type(p) is cls
    assert type(p) is not pathlib.Path
    assert isinstance(p, pathlib.Path)


def test_context_type(tmp_path: pathlib.Path, cls: Any):
    with cls(tmp_path) as p:
        assert type(p) is cls
        assert type(p) is not pathlib.Path
        assert isinstance(p, pathlib.Path)


def test_archive_type(tmp_path: pathlib.Path, cls: Any):
    p = cls(__file__).make_archive(tmp_path.joinpath("test.zip"))
    assert type(p) is cls
    assert type(p) is not pathlib.Path
    assert isinstance(p, pathlib.Path)

    z = p.unpack_archive(tmp_path.joinpath("archive"))
    assert type(z) is cls
    assert type(z) is not pathlib.Path
    assert isinstance(z, pathlib.Path)


def test_move_type(tmp_path: pathlib.Path, cls: Any):
    p = cls(__file__).copy(tmp_path)

    dest = tmp_path.joinpath("test")
    dest.mkdir()

    z = p.move(dest)
    assert type(z) is cls
    assert type(z) is not pathlib.Path
    assert isinstance(z, pathlib.Path)
