import os
from subprocess import CompletedProcess

import pytest

from pathlibutil import Path


@pytest.fixture
def mock_resolve(mocker):
    mock = mocker.patch("pathlib.Path.resolve")
    mock.return_value = Path("//server/temp/file.txt")

    return mock


@pytest.fixture
def mock_run(mocker):
    # Create a CompletedProcess object
    completed_process = CompletedProcess(
        args=["net", "use"],
        returncode=0,
        stdout=r"OK    T:    \\server\temp Microsoft Windows Network",
        stderr=None,
    )

    # Mock subprocess.run() to return the CompletedProcess object
    mock = mocker.patch("subprocess.run", return_value=completed_process)

    return mock


@pytest.fixture
def path(cls):

    yield cls("file.txt")


def test_resolve_default(path, mock_resolve, mock_run):
    assert path.resolve() == Path("//server/temp/file.txt")


def test_resolve_unctrue(path, mock_resolve, mock_run):
    assert path.resolve(unc=True) == Path("//server/temp/file.txt")


def test_resolve_uncfalse_none(path, mock_run, mocker):

    mocker.patch("re.finditer", side_effect=Exception)
    mocker.patch("pathlib.Path.resolve", return_value=path)
    assert path.resolve(unc=False).as_posix() == path.as_posix()


@pytest.mark.skipif(os.name != "nt", reason="Windows only")
def test_resolve_uncfalse(path, mock_resolve, mock_run):
    assert path.resolve(unc=False) == Path("T:/file.txt")
