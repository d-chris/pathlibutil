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


@pytest.mark.parametrize(
    "recursive, result",
    [
        (True, 4),
        (0, 1),
        (1, 3),
        (2, 4),
        (123, 4),
    ],
)
def test_iterdir_recursive(test_dir, recursive, result):

    p = Path(test_dir)

    files = list(p.iterdir(recursive=recursive))

    assert len(files) == result
    assert all(p.is_file() for p in files)


def test_iterdir_exclude(test_dir):
    p = Path(test_dir)

    files = list(
        p.iterdir(recursive=True, exclude_dirs=lambda p: p.name.startswith("sub"))
    )

    assert len(files) == 1


def test_iterdir_exclude_raises(test_dir):
    p = Path(test_dir)

    with pytest.raises(TypeError):
        list(p.iterdir(recursive=True, exclude_dirs=["subdir1"]))
