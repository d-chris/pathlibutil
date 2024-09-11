import itertools
import pathlib
import re
import urllib.parse as up
import urllib.request
from dataclasses import asdict, dataclass, field
from functools import cached_property, wraps
from typing import Any, Dict, Optional, Tuple, TypeVar, Union


@dataclass
class UrlNetloc:
    """
    A dataclass to represent the netloc part of a URL.

    >>> url = UrlNetloc.from_netloc("www.example.com:443")
    >>> url.port = None
    >>> str(url)
    'www.example.com'
    """

    hostname: str
    port: Optional[int] = field(default=None)
    username: Optional[str] = field(default=None)
    password: Optional[str] = field(default=None)

    def __str__(self) -> str:
        return self.netloc

    @property
    def netloc(self) -> str:
        """netloc string representation of the `dataclass`"""

        netloc = ""

        if self.username:
            netloc += self.username

            if self.password:
                netloc += f":{self.password}"

            netloc += "@"

        if ":" in self.hostname:
            netloc += f"[{self.hostname}]"
        else:
            netloc += self.hostname

        if self.port:
            netloc += f":{self.port:d}"

        return netloc

    @classmethod
    def from_netloc(cls, netloc: str, normalize: bool = False) -> "UrlNetloc":
        """Parse a netloc string into a `UrlNetloc` object"""

        if not netloc.startswith("//"):
            netloc = f"//{netloc}"

        url = up.urlparse(netloc)

        hostname = url.hostname

        if normalize is False:
            try:
                pattern = re.escape(url.hostname)
                hostname = re.search(pattern, netloc, re.IGNORECASE).group()
            except AttributeError:
                pass

        return cls(
            hostname=hostname,
            port=url.port,
            username=url.username,
            password=url.password,
        )

    def to_dict(self, prune: bool = False) -> Dict[str, Any]:
        """
        Convert the `UrlNetloc` object to a dictionary

        If `prune` is `True`, remove all key-value pairs from the dict where the value
        is `None`.
        """

        data = asdict(self)

        if not prune:
            return data

        return {k: v for k, v in data.items() if v is not None}


_UrlPath = TypeVar("_UrlPath", bound="UrlPath")


def normalize_url(
    url: str,
    port: bool = False,
    sort: bool = True,
) -> str:
    """
    Function to normalize a URL by converting the scheme and host to lowercase, removing
    port if present, and sorting the query parameters.

    >>> normalize_url("https://www.ExamplE.com:443/Path?b=2&a=1")
    'https://www.example.com/Path?a=1&b=2'
    """

    url = UrlPath(url)

    if port is False:
        ports = {url.scheme.lower(): url.port}
    else:
        ports = {}

    return url.normalize(sort=sort, ports=ports)


def urlpath(func):
    """
    decorator to return a `UrlPath` object from a `urllib.parse.ParseResult` object.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> _UrlPath:
        result = func(self, *args, **kwargs)

        return self.__class__(result.geturl(), **self._kwargs)

    return wrapper


class UrlPath(up.ParseResult):
    """
    Class to manipulate URLs to change the scheme, netloc, path, query, and fragment.

    Wrap the `pathlib.PurePosixPath` methods to return a new `UrlPath` object

    >>> url = UrlPath("https://www.example.com/path/to/file").with_suffix(".txt")
    >>> str(url)
    'https://www.example.com/path/to/file.txt'

    """

    _default_ports = {
        "http": 80,
        "https": 443,
    }

    def __new__(cls, url, **kwargs) -> _UrlPath:
        parsed_url = up.urlparse(url, **kwargs)
        return super().__new__(cls, *parsed_url)

    def __init__(
        self,
        url: str,
        scheme: str = "",
        allow_fragments: bool = True,
    ) -> None:
        """
        Initialize the `UrlPath` object with a URL string.

        A `ValueError` is raised if the URL is not valid.
        """
        self._url = url
        self._kwargs = {
            "scheme": scheme,
            "allow_fragments": allow_fragments,
        }
        self._path = pathlib.PurePosixPath(up.unquote(self.path))

    def __str__(self) -> str:
        return self.normalize()

    def geturl(self, normalize: bool = False) -> str:
        """
        Return a re-combined version of the URL.

        If `normalize` is `True` scheme and netloc is converted  to lowercase,
        default ports are removed and query parameters are sorted.
        """
        if normalize:
            return self.normalize()

        return super().geturl()

    def normalize(self, sort: bool = True, **kwargs) -> str:
        """
        Normalize the URL by converting the scheme and host to lowercase, removing the
        default port if present, and sorting the query parameters.
        """

        ports = kwargs.get("ports", self._default_ports)

        scheme = self.scheme.lower()
        netloc = UrlNetloc.from_netloc(self.netloc, normalize=True)

        try:
            if ports[scheme] == netloc.port:
                netloc.port = None
        except KeyError:
            pass

        path = up.quote(up.unquote(self.path))
        query = up.urlencode(sorted(up.parse_qsl(self.query))) if sort else self.query

        return up.urlunparse(
            (
                scheme,
                str(netloc),
                path,
                self.params,
                query,
                self.fragment,
            )
        )

    def __getattr__(self, attr: str) -> Any:

        try:
            attr = getattr(self._path, attr)
        except AttributeError as e:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{attr}'"
            ) from e

        if not callable(attr):
            return attr

        @wraps(attr)
        def wrapper(*args, **kwargs) -> _UrlPath:
            result = attr(*args, **kwargs)

            return self.with_path(result)

        return wrapper

    @urlpath
    def with_scheme(self, scheme: str) -> _UrlPath:
        """
        Change the scheme of the URL.
        """
        return self._replace(scheme=scheme)

    @urlpath
    def with_netloc(self, netloc: Union[str, UrlNetloc]) -> _UrlPath:
        """
        Change the netloc of the URL.
        """
        return self._replace(netloc=str(netloc))

    @urlpath
    def with_path(self, path: Union[str, pathlib.PurePosixPath]) -> _UrlPath:
        """
        Change the path of the URL.
        """

        try:
            path = path.as_posix()
        except AttributeError as e:
            if not isinstance(path, str):
                raise TypeError(
                    f"Expected str or PurePosixPath, got {type(path)}"
                ) from e

        return self._replace(path=path)

    @urlpath
    def with_params(self, params: str) -> _UrlPath:
        """
        Change the parameters of the URL.
        """
        return self._replace(params=params)

    @urlpath
    def with_query(self, query: str) -> _UrlPath:
        """
        Change the query of the URL.
        """
        return self._replace(query=query)

    @urlpath
    def with_fragment(self, fragment: str) -> _UrlPath:
        """
        Change the fragment of the URL.
        """
        return self._replace(fragment=fragment)

    def with_port(self, port: int) -> _UrlPath:
        """
        change the port in the netloc of the URL.

        If `port` is `None`, the port is removed.
        """

        netloc = UrlNetloc.from_netloc(self.netloc)
        netloc.port = port

        return self.with_netloc(netloc)

    def with_hostname(self, hostname: str) -> _UrlPath:
        """
        change the hostname in the netloc of the URL
        """

        netloc = UrlNetloc.from_netloc(self.netloc)
        netloc.hostname = hostname

        return self.with_netloc(netloc)

    def with_credentials(self, username: str, password: str = None) -> _UrlPath:
        """
        change the username and password in the netloc of the URL

        to change only `username` the `password` must also be provided.

        If `username` is `None`, the credentials are removed.
        """

        netloc = UrlNetloc.from_netloc(self.netloc)
        netloc.username = username
        netloc.password = password

        return self.with_netloc(netloc)

    @cached_property
    def parts(self) -> Tuple[str, ...]:
        """
        return the parts of the path without any '/'.
        """
        return tuple(part for part in self._path.parts if not part.startswith("/"))

    @property
    def anchor(self) -> str:
        """
        The concatenation of the netloc and root of the path.

        >>> UrlPath("//server/root/path/file.txt").anchor
        '//server/root'
        """
        try:
            root = self.parts[0]
        except IndexError:
            root = ""

        return f"//{self.netloc}/{root}"

    def with_anchor(self, anchor: str, root: bool = False, **kwargs) -> _UrlPath:
        """
        Change the anchor of the URL.

        If `root` is `True`, the root of the path will not be removed.

        >>> url = UrlPath("//server/root/path/file.txt")
        >>> url.with_anchor("https://www.server.com").geturl()
        'https://www.server.com/path/file.txt'
        """
        anchor = self.__class__(anchor, **kwargs)

        url = self.with_netloc(anchor.netloc)

        if anchor.scheme != url.scheme:
            url = url.with_scheme(anchor.scheme)

        if root is False:
            parts = url.parts[1:]
        else:
            parts = url.parts

        # if anchor has a path, anchor and url path are concatenated
        if any(anchor.parts):
            return url.with_path("/".join(itertools.chain(anchor.parts, parts)))

        # if root is False, the root of the path is removed
        if root is False:
            return url.with_path("/".join(parts))

        return url

    def exists(self, errors: bool = False, **kwargs) -> bool:
        """
        Check if the URL returns a 200 status code.

        If `errors` is `False`, exceptions are suppressed and `False` is returned.

        For `kwargs` see `urllib.request.urlopen`.
        """
        try:
            with urllib.request.urlopen(self.normalize(False), **kwargs) as response:
                return response.status == 200
        except Exception as e:
            if errors is not False:
                raise e

        return False


__all__ = [
    "UrlNetloc",
    "UrlPath",
    "normalize_url",
]
