import os

import pytest

from pathlibutil import Path


@pytest.fixture
def mock_sys(mocker):
    """Mock sys attributes when script is frozen, e.g. with PyInstaller."""

    mocker.patch("sys.frozen", True, create=True)
    mocker.patch("sys._MEIPASS", "/path/_MEIPASS", create=True)
    mocker.patch("sys.executable", "/path/script.exe", create=True)


def test_cwd_default():
    p = Path.cwd()
    assert isinstance(p, Path)
    assert str(p) == os.getcwd()


def test_cwd_default_frozen(mock_sys):
    p = Path.cwd()
    assert isinstance(p, Path)
    assert str(p) == os.getcwd()


def test_cwd_kwarg():
    """Test for TypeError, because only keyword arguments are supported."""
    with pytest.raises(TypeError):
        Path.cwd(False)


@pytest.mark.parametrize("param", [True, False, "_MEIPASS"])
def test_cwd_param(param):
    p = Path.cwd(frozen=param)
    assert isinstance(p, Path)
    assert str(p) == os.getcwd()


@pytest.mark.parametrize(
    "param, result",
    [
        (True, "/path/"),
        ("_MEIPASS", "/path/_MEIPASS"),
    ],
)
def test_cwd_param_frozen(mock_sys, param, result):
    p = Path.cwd(frozen=param)
    assert p == Path(result)


def test_cwd_param_frozen_false(mock_sys):
    p = Path.cwd(frozen=False)
    assert p == Path(os.getcwd())
