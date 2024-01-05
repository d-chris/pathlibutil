import errno
import hashlib
import itertools
import os
import pathlib
import shutil
import sys
from typing import Dict, Generator, List, Set, Callable


class Path(pathlib.Path):
    """Path inherites from `pathlib.Path` and adds some methods to built-in python functions"""

    _archive_formats: Dict[str, Callable] = {}
    """dict holding function to register shutil archive formats"""

    default_hash = 'md5'
    """default hash algorithm for the class when no algorithm is specified for `hexdigest()` and `verify()`"""

    if sys.version_info < (3, 12):
        _flavour = pathlib._windows_flavour if os.name == 'nt' else pathlib._posix_flavour

    def __init_subclass__(cls, **kwargs) -> None:
        """register archive formats from subclasses"""

        super().__init_subclass__()

        try:
            name = kwargs.pop('archive')
            cls._archive_formats[name] = getattr(
                cls, '_register_archive_format'
            )
        except KeyError:
            pass
        except AttributeError:
            pass

    @property
    def algorithms_available(self) -> Set[str]:
        """
            Set of available algorithms that can be passed to `hexdigest()` and `verify()` method.
        """
        return hashlib.algorithms_available

    def hexdigest(self, algorithm: str = None, /, **kwargs) -> str:
        """
            Returns the hexdigest of the file using the named algorithm (default: `default_hash`).
        """
        try:
            args = (kwargs.pop('length'),)
        except KeyError:
            args = ()

        return hashlib.new(
            name=algorithm or self.default_hash,
            data=self.read_bytes(),
        ).hexdigest(*args)

    def verify(self, hexdigest: str, algorithm: str = None, *, strict: bool = True, **kwargs) -> bool:
        """
            Verifies the hash of the file using the named algorithm (default: `default_hash`).
        """
        _hash = self.hexdigest(algorithm, **kwargs)

        if strict:
            return _hash == hexdigest

        if len(hexdigest) < 7:
            raise ValueError('hashdigest must be at least 7 characters long')

        for a, b in zip(_hash, hexdigest):
            if a != b.lower():
                return False

        return True

    def __enter__(self) -> 'Path':
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
        """
        with self.open(**kwargs) as f:
            yield from iter(f.readline, '')

    def size(self, **kwargs) -> int:
        """
            Returns the size in bytes of a file or directory.
        """
        if self.is_dir():
            return sum([p.size(**kwargs) for p in self.iterdir()])

        return self.stat(**kwargs).st_size

    def copy(self, dst: str, exist_ok: bool = True, **kwargs) -> 'Path':
        """
            Copies the file or directory to a destination path.
        """
        try:
            _path = shutil.copytree(
                self,
                dst,
                dirs_exist_ok=exist_ok,
                **kwargs
            )
        except NotADirectoryError:
            dst = Path(dst, self.name)

            if not exist_ok and dst.exists():
                raise FileExistsError(f'{dst} already exists')

            dst.parent.mkdir(parents=True, exist_ok=True)

            _path = shutil.copy2(
                self,
                dst,
                **kwargs
            )

        return Path(_path)

    def delete(self, *, recursive: bool = False, missing_ok: bool = False, **kwargs) -> None:
        """
            Deletes the file or directory.
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

    def move(self, dst: str) -> 'Path':
        """
            Moves the file or directory to a destination path.
        """
        src = self.resolve(strict=True)
        dst = Path(dst).resolve()
        dst.mkdir(parents=True, exist_ok=True)

        try:
            _path = shutil.move(str(src), str(dst))
        except shutil.Error as e:
            raise OSError(e)

        return Path(_path)

    @staticmethod
    def _find_archive_format(filname: 'Path') -> str:
        """
            Searches for a file the correct archive format.
        """
        ext = "".join(filname.suffixes)

        for name, extensions, _ in shutil.get_unpack_formats():
            if ext in extensions:
                return name

        return "".join(ext.split('.'))

    @classmethod
    def _register_format(cls, format: str) -> None:
        """
            Registers a archive format from `Path._register_<format>_format`.
        """
        try:
            register_format = cls._archive_formats[format]
        except KeyError:
            raise ValueError(f"unknown archive format: '{format}'")
        else:
            register_format()

    def make_archive(self, archivename: str, **kwargs) -> 'Path':
        """
            Creates an archive file (eg. zip) and returns the path to the archive.
        """
        _self = self.resolve(strict=True)
        _archive = Path(archivename).resolve()
        _format = kwargs.pop('format', self._find_archive_format(_archive))

        _ = kwargs.pop('root_dir', None)
        _ = kwargs.pop('base_dir', None)

        for _ in range(2):
            try:
                _archive = shutil.make_archive(
                    base_name=_archive.parent.joinpath(_archive.stem),
                    format=_format,
                    root_dir=_self.parent,
                    base_dir=_self.relative_to(_self.parent),
                    **kwargs
                )

                return Path(_archive)
            except ValueError:
                self._register_format(_format)

    def unpack_archive(self, extract_dir: str, **kwargs) -> 'Path':
        """
            Unpacks an archive file (eg. zip) and returns the path to the extracted files.
        """

        _format = kwargs.pop('format', self._find_archive_format(self))

        for _ in range(2):
            try:
                shutil.unpack_archive(
                    self.resolve(strict=True),
                    extract_dir,
                    format=_format,
                    **kwargs
                )

                return Path(extract_dir)
            except ValueError:
                self._register_format(_format)

    @property
    def archive_formats(self) -> List[str]:
        """
            Returns a list of supported archive formats.
        """
        formats = itertools.chain(
            self._archive_formats.keys(),
            [name for name, _ in shutil.get_archive_formats()]
        )

        return list(formats)


class Register7zFormat(Path, archive='7z'):
    """
        Register 7z archive format using `__init_subclass__` hook.

        To register a new archive format create a subclass of `Path` and implement a `_register_archive_format()` method.

        Example:
        ```python
        class Register7zArchive(Path, archive='7z'):
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
            function to register 7z archive format
        """

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
