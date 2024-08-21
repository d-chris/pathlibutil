import pathlib
import urllib.parse as up
from dataclasses import asdict, dataclass, field
from functools import wraps
from typing import Any, Dict, Optional, TypeVar, Union


@dataclass(kw_only=True)
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

        netloc += self.hostname

        if self.port:
            netloc += f":{self.port:d}"

        return netloc

    @classmethod
    def from_netloc(cls, netloc: str, normalize: bool = False) -> "UrlNetloc":
        """Parse a netloc string into a `UrlNetloc` object"""

        username = None
        password = None
        port = None

        if "@" in netloc:
            userinfo, netloc = netloc.split("@", 1)
            if ":" in userinfo:
                username, password = userinfo.split(":", 1)
            else:
                username = userinfo

        if ":" in netloc:
            hostname, port = netloc.split(":", 1)
            port = int(port)
        else:
            hostname = netloc

        if normalize:
            hostname = hostname.lower()

        return cls(hostname=hostname, port=port, username=username, password=password)

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
    ports: Dict[str, int] = None,
    sort: bool = True,
) -> str:
    """
    Normalize a URL by converting the scheme and host to lowercase, removing the default
    port if present, and sorting the query parameters.

    >>> normalize_url("https://www.ExamplE.com:443/Path?b=2&a=1", ports={"https": 443})
    'https://www.example.com/Path?a=1&b=2'
    """

    return UrlPath(url).normalize(sort=sort, ports=ports)


def urlpath(func):
    """
    decorator to return a `UrlPath` object from a `urllib.parse.ParseResult` object
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)

        return UrlPath(result.geturl(), **self._kwargs)

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
        self._url = url
        self._kwargs = {
            "scheme": scheme,
            "allow_fragments": allow_fragments,
        }
        self._path = pathlib.PurePosixPath(up.unquote(self.path))

    def __str__(self) -> str:
        return self.geturl(normalize=True)

    def geturl(self, normalize: bool = False) -> str:
        """
        Return a re-combined version of the URL.

        If `normalize` is `True` schem and netloc is converted  to lowercase,
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
        netloc = UrlNetloc.from_netloc(self.netloc, normalize=True).netloc

        try:
            if netloc.endswith(f":{ports[scheme]}"):
                netloc = netloc.rsplit(":", 1)[0]
        except KeyError:
            pass

        path = up.quote(up.unquote(self.path))
        query = up.urlencode(sorted(up.parse_qsl(self.query))) if sort else self.query

        return up.urlunparse(
            (
                scheme,
                netloc,
                path,
                self.params,
                query,
                self.fragment,
            )
        )

    def __getattr__(self, attr: str) -> Any:

        attr = getattr(self._path, attr)

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


__all__ = [
    "UrlNetloc",
    "UrlPath",
    "normalize_url",
]
