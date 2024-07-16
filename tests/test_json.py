import pytest

from pathlibutil.json import dump, dumps


@pytest.fixture
def obj(file):
    return [file, {1: file}, "string"]


def test_dumps(obj):

    result = dumps(obj)

    assert isinstance(result, str)


def test_dump(obj, tmp_path):
    file = tmp_path.joinpath("test.json")

    assert not file.exists()

    with file.open("w") as f:
        dump(obj, f)

    assert file.is_file()


@pytest.mark.parametrize(
    "method",
    [
        "load",
        "loads",
        "dump",
        "dumps",
    ],
)
def test_test_method(method):
    import pathlibutil.json as pjson

    assert callable(getattr(pjson, method))
