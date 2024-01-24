import os
import pathlib
import sys
from typing import TypeVar

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
