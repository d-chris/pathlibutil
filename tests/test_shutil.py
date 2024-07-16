import pathlib
import shutil

import pytest

from pathlibutil import Path


def test_copy_file(file: Path, tmp_path: pathlib.Path):
    assert hasattr(Path, "copy")

    p = file.copy(tmp_path)

    assert isinstance(p, Path)
    assert str(p) == str(tmp_path / file.name)
    assert p.exists()

    with pytest.raises(FileExistsError):
        file.copy(tmp_path, exist_ok=False)


def test_copy_directory(file: Path, tmp_path: pathlib.Path):
    file.copy(tmp_path)

    p = Path(tmp_path).copy(tmp_path / "copy")

    assert isinstance(p, Path)
    assert p.is_dir()
    assert p.joinpath(file.name).exists()

    with pytest.raises(FileExistsError):
        Path(tmp_path).copy(tmp_path / "copy", exist_ok=False)


def test_copy_deep(file: Path, tmp_path: pathlib.Path):
    file.copy(tmp_path)

    p = Path(tmp_path).copy(tmp_path / "copy" / "deep")

    assert p.is_dir()
    assert p.joinpath(file.name).is_file()


def test_copy_raises(file: Path, tmp_path: pathlib.Path):
    with pytest.raises(FileNotFoundError):
        Path("notexists").copy(tmp_path)


@pytest.mark.xfail(reason="dst directory will be created when copy a file", strict=True)
def test_copy_mkdir(file: Path, tmp_path: pathlib.Path):
    with pytest.raises(FileNotFoundError):
        file.copy(tmp_path / "not-exists")


def test_delete(file: Path, tmp_path: pathlib.Path):
    assert hasattr(Path, "delete")

    p = file.copy(tmp_path)

    p.delete()
    assert not p.exists()

    with pytest.raises(FileNotFoundError):
        p.delete()


def test_delete_directory(tmp_dirpath: Path):
    with pytest.raises(OSError):
        tmp_dirpath.delete()

    with pytest.raises(TypeError):
        tmp_dirpath.delete(True)

    tmp_dirpath.delete(recursive=True)

    assert not tmp_dirpath.exists()


def test_move_dir(file: Path, tmp_path: pathlib.Path):
    src = tmp_path.joinpath("src")
    src.mkdir()

    shutil.copy(file, src)

    p = Path(src).move(tmp_path / "dst")

    assert p.is_dir()
    assert p.parts[-1] == "src"
    assert p.joinpath(file.name).is_file()


def test_move_file(file: Path, tmp_dirpath: Path):
    src = tmp_dirpath / file.name

    assert src.is_file(), "setup failed"

    dst = src.move(tmp_dirpath / "dst")

    assert src.is_file() == False
    assert dst.is_file() == True

    dst.move(tmp_dirpath)

    assert src.is_file() == True
    assert dst.is_file() == False


def test_move_raises(file: Path, tmp_dirpath: Path):
    with pytest.raises(FileNotFoundError):
        Path("notexists").move(tmp_dirpath)

    src = tmp_dirpath / file.name

    with pytest.raises(OSError):
        src.move(tmp_dirpath)
