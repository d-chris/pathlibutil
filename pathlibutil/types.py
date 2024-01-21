import functools
import re
from typing import Set, Tuple, TypeVar

_ByteInt = TypeVar("_ByteInt", bound="ByteInt")


class ByteInt(int):
    """
    Inherit from `int` with attributes to convert bytes to decimal or binary `units` for
    measuring storage data. These attributes will return a `float`

    >>> ByteInt(1234).kb
    1.234

    f-string formatting is also supported

    >>> f"{ByteInt(6543210):.2mib} mebibytes"
    '6.24 mebibytes'
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
