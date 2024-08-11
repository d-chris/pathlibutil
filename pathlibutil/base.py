import os
import pathlib
import sys
from typing import Generator, TypeVar

_Path = TypeVar("_Path", bound=pathlib.Path)


class BasePath(pathlib.Path):
    """
    Baseclass to inherit from `pathlib.Path`.

    This class is only needed for python versions < 3.12.
    """

    if sys.version_info < (3, 12):
        _flavour = (
            pathlib._windows_flavour if os.name == "nt" else pathlib._posix_flavour
        )

    @classmethod
    def expand(cls, file: str) -> Generator[_Path, None, None]:
        """
        yields only Path object of file names that exists. Supports glob patterns in
        filename as wildcards.

        >>> list(Path.expand(__file__))
        [BasePath('pathlibutil/base.py')]

        >>> list(Path.expand("pathlibutil/*.py")
        [BasePath('pathlibutil/base.py'), BasePath('pathlibutil/json.py'),
        BasePath('pathlibutil/path.py'), BasePath('pathlibutil/types.py'),
        BasePath('pathlibutil/__init__.py')]
        """

        file = cls(file)
        try:
            file.resolve(True)
        except (OSError, FileNotFoundError):
            parent, pattern = file.parent, file.name

            yield from parent.glob(pattern)
        else:
            yield file
