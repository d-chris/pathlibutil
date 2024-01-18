import pathlib

import pytest
from pathlibutil import Path, Register7zFormat


@pytest.mark.parametrize("cls", [Path, Register7zFormat])
def test_return_types(tmp_path: pathlib.Path, cls):
    p = cls(__file__).copy(tmp_path)
    assert type(p) is cls
    assert type(p) is not pathlib.Path

    with cls(tmp_path) as p:
        assert type(p) is cls
        assert type(p) is not pathlib.Path

    p = cls(__file__).make_archive(tmp_path.joinpath("test.zip"))
    assert type(p) is cls

    z = p.unpack_archive(tmp_path.joinpath("archive"))
    assert type(z) is cls
    assert type(z) is not pathlib.Path

    for file in z.iterdir():
        p = file.move(tmp_path.joinpath("moved"))
        assert type(p) is cls
        assert type(p) is not pathlib.Path
        break
