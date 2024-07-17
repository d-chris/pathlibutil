import functools
import os
import re
from datetime import datetime, tzinfo
from typing import Iterable, Set, Tuple, TypeVar

_ByteInt = TypeVar("_ByteInt", bound="ByteInt")
_stat_result = TypeVar("_stat_result", bound="os.stat_result")


class ByteInt(int):
    """
    Inherit from `int` with attributes to convert bytes to decimal or binary `units` for
    measuring storage data. These attributes will return a `float`.

    >>> ByteInt(1234).kb
    1.234

    f-string formatting is also supported

    >>> f"{ByteInt(6543210):.2mib} mebibytes"
    '6.24 mebibytes'

    String representation of `ByteInt` will return the most appropriate decimal unit.

    >>> str(ByteInt(987654))
    '987.7 kb'
    """

    __regex = re.compile(r"(?P<unit>[kmgtpezy]i?b)")

    __bytes = {
        "kb": (10**3, "kilobyte"),
        "mb": (10**6, "megabyte"),
        "gb": (10**9, "gigabyte"),
        "tb": (10**12, "terabyte"),
        "pb": (10**15, "petabyte"),
        "eb": (10**18, "exabyte"),
        "zb": (10**21, "zettabyte"),
        "yb": (10**24, "yottabyte"),
        "kib": (2**10, "kibibyte"),
        "mib": (2**20, "mebibyte"),
        "gib": (2**30, "gibibyte"),
        "tib": (2**40, "tebibyte"),
        "pib": (2**50, "pebibyte"),
        "eib": (2**60, "exbibyte"),
        "zib": (2**70, "zebibyte"),
        "yib": (2**80, "yobibyte"),
    }

    @property
    def units(self) -> Set[str]:
        """
        `decimal` and `binary` units for measuring storage data.

        - `kilobyte` and `kibibyte`
        - `megabyte` and `mebibyte`
        - `gigabyte` and `gibibyte`
        - `terabyte` and `tebibyte`
        - `petabyte` and `pebibyte`
        - `exabyte` and `exbibyte`
        - `zettabyte` and `zebibyte`
        - `yottabyte` and `yobibyte`

        >>> ByteInt().units
        {
            'mib', 'eb', 'kib', 'gb', 'yb', 'mb', 'gib', 'eib',
            'zb', 'yib', 'tib', 'pb', 'zib', 'pib', 'tb', 'kb'
        }
        """
        return set(self.__bytes.keys())

    def __str__(self) -> str:
        return self.string()

    def string(self, decimal=True) -> str:
        """
        Return a string representation of `self` in the most appropriate unit.

        If `decimal` is `False` then binary units will be used instead of `decimal`.

        >>> ByteInt(12346789).string(False)
        '11.77 mib'
        """

        def _decimal(x):
            return "i" not in x[0]

        def _binary(x):
            return x[0].endswith("ib")

        query = _decimal if decimal else _binary

        for unit, (byte, _) in filter(query, self.__bytes.items()):
            value = self / byte

            if 1 <= value < 1000:
                dec = 2 if value < 100 else 1
                return value.__format__(f".{dec}f") + f" {unit}"

        return f"{int(self)} b"

    @classmethod
    def info(cls, unit: str) -> Tuple[int, str]:
        """
        Return a tuple containing `bytes` and `name` for a given `unit`

        >>> ByteInt.info("gib")
        (1073741824, 'gibibyte')
        """
        return cls.__bytes[unit.lower()]

    def __getattr__(self, name: str) -> float:
        """
        Check if unknown attribute is a unit and convert self to that unit.
        """
        try:
            return self / self.__bytes[name.lower()][0]
        except KeyError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

    def __format__(self, __format_spec: str) -> str:
        """
        Support formatting with known units.
        """
        try:
            return super().__format__(__format_spec)
        except ValueError as e:
            match = self.__regex.search(__format_spec)

            try:
                value = getattr(self, match["unit"])
            except TypeError:
                raise e

            return value.__format__(self.__regex.sub("f", __format_spec, 1))

    def __add__(self, other: int) -> _ByteInt:
        """
        b + 1
        """
        return self.__class__(super().__add__(other))

    def __iadd__(self, other: int) -> _ByteInt:
        """
        b += 1
        """
        return self.__add__(other)

    def __sub__(self, other: int) -> _ByteInt:
        """
        b - 1
        """
        return self.__class__(super().__sub__(other))

    def __isub__(self, other: int) -> _ByteInt:
        """
        b -=1
        """
        return self.__sub__(other)

    def __mul__(self, other: int) -> _ByteInt:
        """
        b * 1
        """
        return self.__class__(super().__mul__(other))

    def __imul__(self, other: int) -> _ByteInt:
        """
        b *= 1
        """
        return self.__mul__(other)

    def __floordiv__(self, other: int) -> _ByteInt:
        """
        b // 1
        """
        return self.__class__(super().__floordiv__(other))

    def __ifloordiv__(self, other: int) -> _ByteInt:
        """
        b //= 1
        """
        return self.__floordiv__(other)

    def __mod__(self, other: int) -> _ByteInt:
        """
        b % 1
        """
        return self.__class__(super().__mod__(other))

    def __imod__(self, other: int) -> _ByteInt:
        """
        b %= 1
        """
        return self.__mod__(other)


def byteint(func):
    """
    Decorator to convert a return value of  `int` to a `ByteInt` object. Other return
    values are returned as is.

    ```python
    randbyte = byteint(random.randint)


    @byteint
    def randhexbyte():
        return hex(random.randint(0, 2**32))
    ```

    >>> type(randbyte(0, 2**32))
    <class 'pathlibutil.types.ByteInt'>

    >>> type(randhexbytes())
    <class 'str'>
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> ByteInt:
        value = func(*args, **kwargs)

        if isinstance(value, int):
            return ByteInt(value)

        return value

    return wrapper


class TimeInt(float):
    """
    Inherit from `float` with attributes to convert seconds to `datetime` objects.

    >>> TimeInt(0).datetime
    datetime.datetime(1970, 1, 1, 0, 0)

    >>> TimeInt(0).string('%d.%m.%Y')
    '01.01.1970'

    Return a string representation using `TimeInt.format`.

    >>> str(TimeInt(0))
    '1970-01-01 00:00:00'
    """

    format = "%Y-%m-%d %H:%M:%S"
    """
    Format string to which is uesed to convert `self` to a string. Default: 'isoformat'.
    For more information see `datetime.datetime.strftime`.
    """

    def __new__(cls, value: int, tz: tzinfo = None) -> float:
        """
        Create a new instance from baseclass `int`.
        """
        return super().__new__(cls, value)

    def __init__(self, value: int, tz: tzinfo = None) -> None:
        """
        Create a new instance from baseclass `int` with optional `timezone` info.
        """
        self.timezone = tz
        """
        property for `datetime.timezone` object is set with `__init__` or can be
        changed to different timezones to get the correct string reprensentation. If
        timezone is `None` then the local timezone is used.
        """

    @functools.cached_property
    def datetime(self) -> datetime:
        """
        property returns a `datetime.datetime` object.
        """
        return datetime.fromtimestamp(self, self.timezone)

    def __str__(self) -> str:
        """
        Return a string representation of `datetime` using `self.format`.
        """
        return self.string()

    def string(self, format_string: str = None) -> str:
        """
        Return a string representation of `datetime` using the `format_string`.

        If `format_string` is `None` then `TimeInt.format` is used.
        """
        return self.datetime.strftime(format_string or self.format)


class StatResult:
    """
    Object converts `st_size` to `ByteInt` and
    `st_atime`, `st_mtime`, `st_ctime` and `st_birthtime` to `TimeInt`.

    Inheritance was not possible due `@final` decorator is applied to `os.stat_result`
    to prevent subclassing.
    """

    def __init__(self, stat):
        """
        Wrapper for `os.stat_result`.
        """
        self._obj = stat

    def __getattr__(self, name):
        """
        Forward all unknown attributes to `self._obj`.
        """
        attr = getattr(self._obj, name)

        if isinstance(attr, int):
            if name == "st_size":
                return ByteInt(attr)
        elif isinstance(attr, float):
            if name in ("st_atime", "st_mtime", "st_ctime", "st_birthtime"):
                return TimeInt(attr)

        return attr

    def __str__(self) -> str:
        """
        Return a string of `os.stat_result` object.
        """
        return str(self._obj)

    def __repr__(self) -> str:
        """
        Return representation of `os.stat_result` object.
        """
        return repr(self._obj)

    def __dir__(self) -> Iterable[str]:
        """
        Return a list of attributes of `os.stat_result` object.
        """
        return dir(self._obj)

    def __len__(self) -> int:
        """
        Return length of `os.stat_result` object.
        """
        return len(self._obj)

    @property
    def stat_result(self) -> os.stat_result:
        """
        Return the wrapped `os.stat_result` object.
        """
        return self._obj
