import itertools
import pathlib
import shutil

import pytest

from pathlibutil import Path


@pytest.mark.parametrize("arg", Path().archive_formats)
def test_archive_format(arg, tmp_path: pathlib.Path):
    """check if suffix from archivename is as specified when format is given"""

    archive = tmp_path.joinpath("test.abc")

    try:
        file = Path(__file__).make_archive(archive, format=arg)
    except ModuleNotFoundError:
        pytest.skip(f"Module for {arg} not found")
    else:
        assert file.is_file()
        assert file.suffixes == archive.suffixes


def test_archive_exists(tmp_path: pathlib.Path):
    """check if FileExistsError is raised when archivename exists"""

    archive = tmp_path.joinpath("test.zip")

    archive.touch()

    with pytest.raises(FileExistsError):
        Path(__file__).make_archive(archive)


def test_archive_existsok(tmp_path: pathlib.Path):
    """check if file is overwritten when exists_ok is True"""

    archive = tmp_path.joinpath("test.zip")

    archive.touch()

    assert archive.is_file()

    file = Path(__file__).make_archive(archive, exists_ok=True)

    assert file == archive


@pytest.mark.parametrize(
    "suffix", itertools.chain(*[ext for _, ext, _ in shutil.get_unpack_formats()])
)
def test_archive_suffix(suffix, tmp_path: pathlib.Path):
    """check archive with suffixes"""

    archive = tmp_path.joinpath("test").with_suffix(suffix)

    file = Path(__file__).make_archive(archive)
    assert str(file).endswith(suffix)
