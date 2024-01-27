import pytest

from pathlibutil import Path


@pytest.fixture(
    params=[
        ("a/b/c", "a/c/d", "../../b/c"),
        ("a/b/c/d", "a/b/e/f", "../../c/d"),
        ("a/b/c", "d/e/f", "../../../a/b/c"),
    ]
)
def relative_up(request):
    return request.param


@pytest.fixture(
    params=[
        ("a/b/c", "a/b/c", ""),
        ("a/b/c", "a/b/c", "."),
        ("a/b/c", "a/b", "c"),
        ("a/b/c", "a", "b/c"),
        ("a/b/c", ".", "a/b/c"),
        ("a/b/c", "", "a/b/c"),
    ]
)
def relative_down(request):
    return request.param


def test_relative_to(relative_down):
    start, path, result = relative_down

    p = Path(start).relative_to(path)
    assert p == Path(result)


def test_relative_up_bool(relative_up):
    start, path, result = relative_up

    p = Path(start).relative_to(path, walk_up=True)
    assert p == Path(result)


def test_relative_up_int(relative_up):
    start, path, result = relative_up

    p = Path(start).relative_to(path, walk_up=3)
    assert p == Path(result)


def test_relative_raises(relative_up):
    start, path, _ = relative_up

    with pytest.raises(ValueError):
        Path(start).relative_to(path)


def test_relative_raises_up_int(relative_up):
    start, path, _ = relative_up

    with pytest.raises(ValueError):
        Path(start).relative_to(path, walk_up=1)
