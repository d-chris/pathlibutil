import hashlib
import os
import pathlib
import random
from types import GeneratorType
from unittest.mock import Mock

import pytest

from pathlibutil import Path


@pytest.fixture(scope='function')
def algorithm() -> str:
    """random hash algorithm for one test without shake"""
    return random.choice(
        [
            a for a in hashlib.algorithms_available
            if not a.startswith('shake')
        ]
    )


@pytest.fixture(scope='function')
def shake() -> str:
    """random shake algorithm for one test"""
    return random.choice(
        [
            a for a in hashlib.algorithms_available
            if a.startswith('shake')
        ]
    )


@pytest.fixture(scope='function')
def length() -> int:
    """random length between 8 and 16 for shake algorithms"""
    return random.randint(8, 16)


@pytest.fixture(autouse=True)
def mock_hexdigest(mocker) -> Mock:
    mock_hashlib_new = mocker.patch('hashlib.new')

    mock = Mock()
    mock.hexdigest.return_value = '0123456789abcdef'

    mock_hashlib_new.return_value = mock

    yield mock


def test_hexdigest_default(file: Path):
    assert hasattr(Path, 'hexdigest')

    p = file.hexdigest()

    assert isinstance(p, str)
    assert p == hashlib.new('md5', open(__file__, 'rb').read()).hexdigest()


def test_hexdigest_hash(file: Path, algorithm: str):
    hash = hashlib.new(algorithm, open(__file__, 'rb',).read()).hexdigest()

    file.default_hash = algorithm

    p = file.hexdigest()

    assert p == hash


def test_hexdigest_random(file: Path, algorithm: str):

    p = file.hexdigest(algorithm)

    assert p == hashlib.new(algorithm, open(__file__, 'rb').read()).hexdigest()


def test_hexdigest_length(file: Path, shake: str, length: int):

    with pytest.raises(TypeError):
        _ = file.hexdigest(shake, length)

    p = file.hexdigest(shake, length=length)

    assert p == hashlib.new(
        shake,
        open(__file__, 'rb').read()
    ).hexdigest(length)


def test_algorithms_available(file: Path):
    assert hasattr(Path, 'algorithms_available')

    p = file.algorithms_available

    assert isinstance(p, set)
    assert hashlib.algorithms_available == p


def test_read_lines(file: Path):
    assert hasattr(Path, 'read_lines')

    p = file.read_lines()

    assert isinstance(p, GeneratorType)
    assert "".join(p) == open(str(file)).read()


def test_default_hash(file: Path):
    assert hasattr(Path, 'default_hash')

    assert file.default_hash == 'md5'


def test_context_manager(tmp_path: pathlib.Path):
    assert hasattr(Path, '__enter__')
    assert hasattr(Path, '__exit__')

    with Path(tmp_path) as p:
        assert isinstance(p, Path)
        assert str(p) == str(tmp_path)
        assert str(os.getcwd()) == str(tmp_path)


def test_context_manager_raises(tmp_path: pathlib.Path):

    with pytest.raises(FileNotFoundError):
        with Path(tmp_path / 'nonexistent'):
            pass

    file = tmp_path / 'file.txt'
    file.touch()

    with pytest.raises(NotADirectoryError):
        with Path(file):
            pass


def test_default_hash_classvar(cls: Path, algorithm: str):
    assert cls.default_hash == 'md5'

    p = cls(__file__)

    cls.default_hash = algorithm

    assert p.default_hash == algorithm
    assert p.hexdigest() == hashlib.new(
        algorithm, open(__file__, 'rb').read()).hexdigest()


def test_size(file: Path):
    assert hasattr(Path, 'size')

    assert file.size() == os.stat(str(file)).st_size


def test_size_dir(tmp_path: pathlib.Path):
    assert Path(tmp_path).size() == 0

    tmp_path.joinpath('tempdir').mkdir()
    assert Path(tmp_path).size() == 0

    assert tmp_path.joinpath('file.txt').write_text(
        'ipsum lorem') == Path(tmp_path).size()


def test_size_raises(tmp_path: pathlib.Path):

    with pytest.raises(FileNotFoundError):
        _ = Path(tmp_path / 'nonexistent').size()


def test_verify(file: Path, algorithm: str):
    assert hasattr(Path, 'verify')

    hashsum = hashlib.new(algorithm, open(__file__, 'rb').read()).hexdigest()

    assert file.verify(hashsum, algorithm) == True
    assert file.verify(hashsum, algorithm=algorithm, strict=True) == True

    assert file.verify(hashsum.upper(), algorithm) == False
    assert file.verify(hashsum[:len(hashsum) - 1], algorithm) == False

    with pytest.raises(ValueError):
        _ = file.verify('', strict=False)

    with pytest.raises(TypeError):
        _ = file.verify(None, strict=False)


def test_verify_classvar(file: Path):
    hashsum = hashlib.new('md5', open(__file__, 'rb').read()).hexdigest()

    assert file.verify(hashsum) == True
    assert file.verify(hashsum[:8], strict=False) == True

    assert file.verify(hashsum[:4]+hashsum[:4], strict=False) == False


def test_verify_strict(file: Path, algorithm: str):

    hashsum = hashlib.new(algorithm, open(__file__, 'rb').read()).hexdigest()

    with pytest.raises(TypeError):
        _ = file.verify(hashsum, algorithm, False)

    assert file.verify(hashsum.upper(), algorithm, strict=False) == True

    assert file.verify(hashsum[:7], algorithm, strict=False) == True

    with pytest.raises(ValueError):
        _ = file.verify(hashsum[:6], strict=False)
