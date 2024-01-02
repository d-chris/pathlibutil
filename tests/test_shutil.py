import pytest
import pathlib

from pathlibutil import Path


def test_copy_file(file: Path, tmp_path: pathlib.Path):
    assert hasattr(Path, 'copy')

    p = file.copy(tmp_path)

    assert isinstance(p, Path)
    assert str(p) == str(tmp_path / file.name)
    assert p.exists()

    with pytest.raises(FileExistsError):
        file.copy(tmp_path, exist_ok=False)


def test_copy_directory(file: Path, tmp_path: pathlib.Path):

    file.copy(tmp_path)

    p = Path(tmp_path).copy(tmp_path / 'copy')

    assert isinstance(p, Path)
    assert p.is_dir()
    assert p.joinpath(file.name).exists()

    with pytest.raises(FileExistsError):
        Path(tmp_path).copy(tmp_path / 'copy', exist_ok=False)


def test_copy_deep(file: Path, tmp_path: pathlib.Path):

    file.copy(tmp_path)

    p = Path(tmp_path).copy(tmp_path / 'copy' / 'deep')

    assert p.is_dir()
    assert p.joinpath(file.name).is_file()


def test_copy_raises(file: Path, tmp_path: pathlib.Path):

    with pytest.raises(FileNotFoundError):
        Path('notexists').copy(tmp_path)


@pytest.mark.xfail(reason='dst directory will be created when copy a file')
def test_copy_mkdir(file: Path, tmp_path: pathlib.Path):
    with pytest.raises(FileNotFoundError):
        file.copy(tmp_path / 'not-exists')
