import pytest

from pathlibutil import Path


@pytest.mark.parametrize(
    "file, suffix, result",
    [
        ("test", ".a", "test.a"),
        ("test.a", "", "test"),
        ("test.a.b", "", "test.a"),
        ("test.a", ".b", "test.b"),
        ("test.a", ".b.c", "test.b.c"),
        ("test.a.b", ".c", "test.a.c"),
        ("test.a.b", ".c.d", "test.a.c.d"),
        ("test", [".a", ".b"], "test.a.b"),
        ("test.a", [], "test"),
        ("test.a.b", [], "test"),
        ("test.a", [""], "test"),
        ("test.a.b", ["", ""], "test"),
        ("test.a", [".b"], "test.b"),
        ("test.a", [".b", ".c"], "test.b.c"),
        ("test.a.b", [".c"], "test.c"),
        ("test.a.b", [".c", ".1"], "test.c.1"),
        ("test.a.b", [".c.d"], "test.c.d"),
    ],
)
def test_with_suffixes(file, suffix, result):
    assert Path(file).with_suffix(suffix) == Path(result)


@pytest.mark.parametrize(
    "suffix", ["a", ["a"], [".a", "b"], [".a", ".b", ""], ["a", ".b"]]
)
def test_with_suffix_raises(suffix):
    with pytest.raises(ValueError):
        Path(__file__).with_suffix(suffix)
