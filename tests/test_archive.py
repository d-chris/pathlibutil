import shutil
import pytest
from zipfile import ZipFile
import pathlib

from pathlibutil import Path


def test_archive_file(tmp_file: Path, tmp_path: pathlib.Path):
    assert hasattr(Path, 'make_archive')

    archive = tmp_file.make_archive(tmp_path.joinpath('archive.zip'))

    assert isinstance(archive, Path)
    assert archive.is_file()

    for info in ZipFile(archive).filelist:
        assert info.filename == tmp_file.name


def test_archive_raises(cls: Path, tmp_file: Path, tmp_path: pathlib.Path):
    archive = str(tmp_path.joinpath('archive.zip'))

    with pytest.raises(ValueError):
        tmp_file.make_archive(archive, format='rar')

    with pytest.raises(FileNotFoundError):
        cls('notexsist').make_archive(archive)


def test_archive_register(tmp_file: Path, tmp_path: pathlib.Path):

    archive = tmp_file.make_archive(tmp_path.joinpath('archive.7z'))

    assert archive.is_file()
    assert archive.suffix == '.7z'


def test_archive_format(cls: Path):
    assert hasattr(cls, 'archive_formats')

    format = cls().archive_formats
    assert isinstance(format, list)

    for name, _ in shutil.get_archive_formats():
        assert name in format


def test_pack_unpack_directory(cls: Path, tmp_path: pathlib.Path):
    # create a test folder with 3 files using os functions
    files = [
        'test/test1.txt',
        'test/test2/',
        'test/test3/test3.txt'
    ]

    for file in files:
        p = tmp_path.joinpath(file)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(str(file))

    archive = tmp_path.joinpath('archive.zip')
    root = tmp_path.joinpath('test')

    assert archive.exists() == False
    assert root.is_dir() == True

    cls(root).make_archive(archive)
    shutil.rmtree(str(root))

    assert root.exists() == False
    assert archive.is_file() == True

    cls(archive).unpack_archive(tmp_path)
    archive.unlink()

    assert archive.exists() == False
    assert root.is_dir() == True


def test_pack_unpack_file(cls: Path, tmp_file: Path, tmp_path: pathlib.Path):
    assert hasattr(Path, 'unpack_archive')

    # zip name
    archive = str(tmp_path.joinpath('archive.zip').resolve())

    # create zip and delete tmp_file
    zip = tmp_file.make_archive(archive)
    tmp_file.unlink()
    assert tmp_file.is_file() == False
    assert zip.is_file()

    # restore tmp_file from hip and delete zip
    zip.unpack_archive(tmp_path)
    zip.unlink()
    assert zip.is_file() == False
    assert tmp_file.is_file() == True


def test_unpack_archive_raises(tmp_path: pathlib.Path):

    with pytest.raises(FileNotFoundError):
        Path(tmp_path.joinpath('archive.zip')).unpack_archive(tmp_path)

    with pytest.raises(ValueError):
        Path(__file__).unpack_archive(tmp_path, format='rar')
