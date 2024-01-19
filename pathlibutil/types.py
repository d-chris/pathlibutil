import functools
import re


class ByteSize(int):
    __regex = re.compile(r"(?P<unit>[kmgtpezy]i?b)")

    __bytes = {
        "kb": 10**3,  # kilobyte
        "mb": 10**6,  # megabyte
        "gb": 10**9,  # gigabyte
        "tb": 10**12,  # terabyte
        "pb": 10**15,  # petabyte
        "eb": 10**18,  # exabyte
        "zb": 10**21,  # zettabyte
        "yb": 10**24,  # yottabyte
        "kib": 2**10,  # kibibyte
        "mib": 2**20,  # mebibyte
        "gib": 2**30,  # gibibyte
        "tib": 2**40,  # tebibyte
        "pib": 2**50,  # pebibyte
        "eib": 2**60,  # exbibyte
        "zib": 2**70,  # zebibyte
        "yib": 2**80,  # yobibyte
    }

    def __getattr__(self, name: str) -> float:
        """
        check if unknown attribute is a unit and convert self to that unit
        """
        try:
            return float(self) / self.__bytes[name.lower()]
        except KeyError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

    def __format__(self, __format_spec: str) -> str:
        """
        support formatting with with known units
        """
        try:
            return super().__format__(__format_spec)
        except ValueError:
            match = self.__regex.search(__format_spec)

            try:
                value = getattr(self, match["unit"])
            except TypeError:
                raise ValueError(
                    f"Unknown format code '{__format_spec}' for object of type '{self.__class__.__name__}'"
                )

            return value.__format__(self.__regex.sub("f", __format_spec, 1))


def bytesize(func):
    """wrapper to convert return value to ByteSize"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> ByteSize:
        size = func(*args, **kwargs)
        return ByteSize(size)

    return wrapper
