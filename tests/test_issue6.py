import pytest
import pathlib
from pathlibutil import Path


@pytest.mark.xfail(reason="Issue #6 not implemented yet", strict=True)
@pytest.mark.parametrize("arg", Path().archive_formats)
def test_archive_suffix(arg, tmp_path: pathlib.Path):
    """check if suffix from archivename is as specified when format is given"""

    archive = tmp_path.joinpath("test.abc")

    try:
        file = Path(__file__).make_archive(archive, format=arg)
    except ModuleNotFoundError:
        pytest.xfail(f"Module for {arg} not found")
    else:
        assert file.is_file()
        assert file.suffixes == archive.suffixes
