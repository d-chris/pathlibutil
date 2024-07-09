import pytest

from pathlibutil import Path


@pytest.fixture
def test_dir(tmp_path):
    files = [
        "file1.txt",
        "subdir1/file2.txt",
        "subdir2/",
        "subdir3/file3.txt",
        "subdir3/subdir31/file31.txt",
        "subdir4/subdir41/",
    ]

    for file in map(tmp_path.joinpath, files):
        if file.suffix:
            file.parent.mkdir(parents=True, exist_ok=True)
            file.touch()
        else:
            file.mkdir(parents=True, exist_ok=True)

    yield tmp_path


def test_walk():
    assert hasattr(Path, "walk")


def test_walks(test_dir):

    p = Path(test_dir)
    for dirpath, dirnames, filenames in p.walk():
        assert isinstance(dirpath, Path)
        assert all(isinstance(d, str) for d in dirnames)
        assert all(isinstance(f, str) for f in filenames)


def test_iderdir_recursive_raises():

    with pytest.raises(TypeError):
        Path().iterdir(True)


def test_iterdir_recursive(test_dir):

    p = Path(test_dir)
    result = p.iterdir(recursive=True)

    assert all(p.is_file() for p in result)
