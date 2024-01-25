import errno
import hashlib
import itertools
import os
import shutil
from typing import Callable, Dict, Generator, List, Set, Union

from pathlibutil.base import BasePath, _Path
from pathlibutil.types import ByteInt, StatResult, _stat_result, byteint


class Path(BasePath):
    """
    Path inherites from `pathlib.Path` and adds some methods to built-in python
    functions.

    - To Register new archive formats for `make_archive` and `unpack_archive` see
    example `Register7zFormat`

    - Contextmanger lets you change the current working directory.
    ```python
    with Path('path/to/directory') as cwd:
        print(f'current working directory: {cwd}')
    ```
    """

    _archive_formats: Dict[str, Callable] = {}
    """
    Dict holding function to register shutil archive formats.
    """

    default_hash: str = "md5"
    """
    Default hash algorithm for `__class__`.

    If no `algorithm` parameter is specified with `hexdigest()` or `verify()` this will
    be the default
    """

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Register archive formats from subclasses.
        """

        super().__init_subclass__()

        try:
            name = kwargs.pop("archive")
            cls._archive_formats[name] = getattr(cls, "_register_archive_format")
        except KeyError:
            pass
        except AttributeError:
            pass

    @property
    def algorithms_available(self) -> Set[str]:
        """
        Set of `hashlib.algorithms_available` that can be passed to `hexdigest()`,
        `verify()` method as `algorithm` parameter or to set the `default_hash`
        algorithm of the `__class__`.

        >>> Path().algorithms_available
        {
            'sha384', 'sha3_512', 'blake2b', 'md5-sha1', 'sha3_256', 'sha3_384',
            'sha512', 'sha512_256', 'sha3_224', 'sha1', 'md5', 'ripemd160', 'blake2s',
            'sha256', 'shake_256', 'shake_128', 'sha224', 'sha512_224', 'sm3'
        }
        """
        return hashlib.algorithms_available

    def hexdigest(self, algorithm: str = None, /, **kwargs) -> str:
        """
        Returns the hexdigest of the file using the named algorithm (default:
        `default_hash`).

        A `FileNotFoundError` is raised if the file does not exist or its a directory.

        Some hashes will raise `TypeError` if the `length` argument is missing, use
        `**kwargs` for this purpose.
        """
        if not self.is_file():
            raise FileNotFoundError(f"'{self}' is not an existing file")

        try:
            args = (kwargs.pop("length"),)
        except KeyError:
            args = ()

        return hashlib.new(
            name=algorithm or self.default_hash,
            data=self.read_bytes(),
        ).hexdigest(*args)

    def verify(
        self, digest: str, algorithm: str = None, *, strict: bool = True, **kwargs
    ) -> bool:
        """
        Verifies the hash of the file using the named algorithm (default:
        `default_hash`).

        If `strict` is `True` the hash must match exactly.

        If `strict` is `False` the hash is compared character by character until
        `digest` is exhausted.
        - a `ValueError` is raised if `digest` is shorter than 7 characters.
        - comparison is case-insensitive

        For `**kwargs` see `hexdigest()`.
        """
        _hash = self.hexdigest(algorithm, **kwargs)

        if strict:
            return _hash == digest

        if len(digest) < 7:
            raise ValueError("hashdigest must be at least 7 characters long")

        for a, b in zip(_hash, digest):
            if a != b.lower():
                return False

        return True

    def __enter__(self) -> _Path:
        """
        Contextmanager to changes the current working directory.
        """
        cwd = os.getcwd()

        try:
            os.chdir(self)
        except Exception as e:
            raise e
        else:
            self.__stack = cwd

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Restore previous working directory.
        """
        try:
            os.chdir(self.__stack)
        finally:
            del self.__stack

    def read_lines(self, **kwargs) -> Generator[str, None, None]:
        """
        Iterates over all lines of the file until EOF is reached.

        For `**kwargs` see `pathlib.Path.open()`.
        """
        with self.open(**kwargs) as f:
            yield from iter(f.readline, "")

    @byteint
    def size(self, **kwargs) -> ByteInt:
        """
        Returns the size in bytes of a file or directory.

        For `**kwargs` see `pathlib.Path.stat()`.
        """
        if self.is_dir():
            return sum([p.size(**kwargs) for p in self.iterdir()])

        return super().stat(**kwargs).st_size

    def copy(self, dst: str, exist_ok: bool = True, **kwargs) -> _Path:
        """
        Copies the file or directory to a destination directory, if it is missing it
        will be created.

        If `exist_ok` is `False` and `dst` already exists a `FileExistsError` is raised.

        For `**kwargs` see `shutil.copy2()` for files and `shutil.copytree()` for
        directories.
        """
        try:
            _path = shutil.copytree(self, dst, dirs_exist_ok=exist_ok, **kwargs)
        except NotADirectoryError:
            dst = Path(dst, self.name)

            if not exist_ok and dst.exists():
                raise FileExistsError(f"{dst} already exists")

            dst.parent.mkdir(parents=True, exist_ok=True)

            _path = shutil.copy2(self, dst, **kwargs)

        return self.__class__(_path)

    def delete(
        self, *, recursive: bool = False, missing_ok: bool = False, **kwargs
    ) -> None:
        """
        Deletes the file or directory.

        If `missing_ok` is `False` a `FileNotFoundError` is raised if the file or
        directory does not exist.

        If `recursive` is `False` an `OSError` is raised if the directory is not empty.

        If `recursive` is `True` the directory will be deleted with all its content
        (files and subdirectories).
        - `**kwargs` are passed on to `shutil.rmtree()`
        """
        try:
            self.rmdir()
        except NotADirectoryError:
            self.unlink(missing_ok)
        except FileNotFoundError as e:
            if not missing_ok:
                raise e
        except OSError as e:
            if not recursive or e.errno != errno.ENOTEMPTY:
                raise e

            shutil.rmtree(self, **kwargs)

    def move(self, dst: str) -> _Path:
        """
        Moves the file or directory into the destination directory.

        If `dst` does not exist it will be created.

        An `OSError` is raised if `shutil.move()` fails.
        """
        src = self.resolve(strict=True)
        dst = Path(dst).resolve()
        dst.mkdir(parents=True, exist_ok=True)

        try:
            _path = shutil.move(str(src), str(dst))
        except shutil.Error as e:
            raise OSError(e)

        return self.__class__(_path)

    @staticmethod
    def _find_archive_format(filename: _Path) -> str:
        """
        Searches for a file the correct archive format.
        """
        ext = "".join(filename.suffixes)

        for name, extensions, _ in shutil.get_unpack_formats():
            if ext in extensions:
                return name

        return "".join(ext.split("."))

    @classmethod
    def _register_format(cls, format: str) -> None:
        """
        Registers a archive format from `_archive_formats`.
        """
        try:
            register_format = cls._archive_formats[format]
        except KeyError:
            raise ValueError(f"unknown archive format: '{format}'")
        else:
            register_format()

    def make_archive(
        self, archivename: str, *, exists_ok: bool = False, **kwargs
    ) -> _Path:
        """
        Creates an archive file (eg. zip) and returns the path to the archive.

        If `exists_ok` is `False` a `FileExistsError` is raised if the archive file
        already exists.

        If `exists_ok` is `True` the existing archive file will be deleted before
        creating the new one.

        For `**kwargs` see `shutil.make_archive()`.
        - `root_dir` and `base_dir` will be resolved automatically
        - `format` will be determined by the file suffix
        - It can be overwritten with an `format` keyword-argument.
        - a `ValueError` is raised if the `format` is unknown.

        >>> Path(__file__).make_archive('test.tar.gz')
        Path('test.tar.gz')

        >>> Path(__file__).make_archive('test.zpy', format='zip')
        Path('test.zpy')
        """

        def _archive_exists(file: str, exists_ok: bool) -> _Path:
            """
            Returns a `Path` object of the archive file or raises a `FileExistsError`
            If `exists_ok` is `True` the file will be deleted.
            """
            file = self.__class__(file).resolve()

            if file.exists():
                if not exists_ok:
                    raise FileExistsError(f"{file} already exists")

                file.unlink()

            return file

        def _archive_filename(expect: Path, real: str) -> _Path:
            """
            Check if the expected archive filename matches the real filename.
            If not try to rename the real filename.
            """
            file = self.__class__(real).resolve(True)

            if file.suffixes != expect.suffixes:
                return file.rename(expect)

            return file

        _self = self.resolve(strict=True)
        _filename = _archive_exists(archivename, exists_ok)
        _format = kwargs.pop("format", self._find_archive_format(_filename))

        _ = kwargs.pop("root_dir", None)
        _ = kwargs.pop("base_dir", None)

        for _ in range(2):
            try:
                _archive = shutil.make_archive(
                    base_name=_filename.with_suffix([]),
                    format=_format,
                    root_dir=_self.parent,
                    base_dir=_self.relative_to(_self.parent),
                    **kwargs,
                )

                break
            except ValueError:
                self._register_format(_format)

        return _archive_filename(_filename, _archive)

    def unpack_archive(self, extract_dir: str, **kwargs) -> _Path:
        """
        Unpacks an archive file (eg. zip) into a directory and returns the path to the
        extracted files.

        For `**kwargs` see `shutil.unpack_archive()`.
        - `format` will be determined by the file suffix
        - It can be overwritten with an `format` keyword-argument.
        - a `ValueError` is raised if the `format` is unknown.

        >>> Path('test.tar.gz').unpack_archive('test')
        Path('test')

        >>> Path('test.zpy').unpack_archive('test', format='zip')
        Path('test')
        """

        _format = kwargs.pop("format", self._find_archive_format(self))

        for _ in range(2):
            try:
                shutil.unpack_archive(
                    self.resolve(strict=True), extract_dir, format=_format, **kwargs
                )

                return self.__class__(extract_dir)
            except ValueError:
                self._register_format(_format)

    @property
    def archive_formats(self) -> Set[str]:
        """
        Returns a set with names of the supported archive formats.

        The set contains all built-in formats from `shutil.get_archive_formats()`
        and all formats registered by subclasse
        (eg. pathlibutil.path.Register7zFormat).

        >>> Path().archive_formats
        {'xztar', 'bztar', 'gztar', 'zip', 'tar', '7z'}
        """
        formats = itertools.chain(
            self._archive_formats.keys(),
            [name for name, _ in shutil.get_archive_formats()],
        )

        return set(formats)

    def stat(self, **kwargs) -> _stat_result:
        """
        Returns a `StatResult` object which modifies following attributes:

        - `st_size` is wrapped in `ByteInt`
        - `st_atime`, `st_mtime`, `st_ctime`, `st_birthtime` are wrapped in `TimeInt`

        For `**kwargs` see `pathlib.Path.stat()`.
        """
        return StatResult(super().stat(**kwargs))

    def with_suffix(self, suffix: Union[str, List[str]]) -> _Path:
        """
        Return a new `Path` with changed suffix or remove it when its an empty
        string.

        >>> Path('test.a.b').with_suffix('.c')
        Path('test.a.c')

        >>> Path('test.a.b').with_suffix('')
        Path('test.a')

        Multiple suffixes can be changed at once by passing a list of suffixes.
        With a empty list all suffixes will be removed.

        >>> Path('test.a.b').with_suffix(['.c', '.d'])
        Path('test.c.d')

        >>> Path('test.a.b').with_suffix([])
        Path('test')
        """

        try:
            return super().with_suffix(suffix)
        except (AttributeError, TypeError):
            if isinstance(suffix, list) and not suffix:
                suffix = ""
            elif all(s.startswith(".") for s in suffix):
                suffix = "".join(suffix)
            elif all(not s for s in suffix):
                suffix = ""
            else:
                raise ValueError(f"Invalid suffix '{suffix}'")

            end = -1 * len(self.suffixes) or None
            name = self.name.split(".")[0:end]
            stem = self.parent.joinpath("".join(name))
            return super(Path, stem).with_suffix(suffix)


class Register7zFormat(Path, archive="7z"):
    """
    Register 7z archive format using `__init_subclass__` hook.

    To register a new archive format just inherit a subclass from `Path` with an
    argument of `archive` specifying the suffix of the archive without any dots (eg.
    filename: **archive.foo.bar** -> argument: `archive='foobar'`) and implement a
    `_register_archive_format()` method using `shutil.register_archive_format()` and
    `shutil.register_unpack_format()` functions.

    The `_register_archive_format()` method will be called automatically with the first
    call of `make_archive()` or `unpack_archive()`.

    Example:
    ```python
    class Register7zArchive(pathlibutil.Path, archive='7z'):
        @classmethod
        def _register_archive_format(cls):
            try:
                from py7zr import pack_7zarchive, unpack_7zarchive
            except ModuleNotFoundError:
                raise ModuleNotFoundError('pip install pathlibutil[7z]')
            else:
                shutil.register_archive_format(
                    '7z', pack_7zarchive, description='7zip archive'
                )
                shutil.register_unpack_format(
                    '7z', ['.7z'], unpack_7zarchive
                )
    ```
    """

    @classmethod
    def _register_archive_format(cls):
        """
        Function to register 7z archive format.
        """

        try:
            from py7zr import pack_7zarchive, unpack_7zarchive
        except ModuleNotFoundError:
            raise ModuleNotFoundError("pip install pathlibutil[7z]")
        else:
            shutil.register_archive_format(
                "7z", pack_7zarchive, description="7zip archive"
            )
            shutil.register_unpack_format("7z", [".7z"], unpack_7zarchive)
