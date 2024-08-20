import pathlib
import urllib.parse as up
from functools import wraps
from typing import Any, Dict, TypeVar, Union

_UrlPath = TypeVar("_UrlPath", bound="UrlPath")


def normalize_url(
    url: Union[str, up.ParseResult],
    ports: Dict[str, int] = None,
    sort: bool = True,
) -> str:
    """
    Normalize a URL by converting the scheme and host to lowercase, removing the default
    port if present, and sorting the query parameters.

    >>> normalize_url("https://www.ExamplE.com:443/Path?b=2&a=1", ports={"https": 443})
    'https://www.example.com/Path?a=1&b=2'
    """

    if not isinstance(url, up.ParseResult):
        url = up.urlparse(url)

    # Convert scheme and host to lowercase
    scheme = url.scheme.lower()
    netloc = url.netloc.lower()

    if ports is not None:
        try:
            if netloc.endswith(f":{ports[scheme]}"):
                netloc = netloc.rsplit(":", 1)[0]
        except KeyError:
            pass

    # Ensure the path is properly encoded
    path = up.quote(up.unquote(url.path))
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    query = up.urlencode(sorted(up.parse_qsl(url.query))) if sort else url.query

    # Reconstruct the URL
    return up.urlunparse(
        (
            scheme,
            netloc,
            path,
            url.params,
            query,
            url.fragment,
        )
    )


class UrlPath(up.ParseResult):

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
        if normalize:
            return normalize_url(self, ports=self._default_ports, sort=True)

        return super().geturl()

    def __getattr__(self, attr: str) -> Any:
        attr = getattr(self._path, attr)

        if not callable(attr):
            return attr

        @wraps(attr)
        def wrapper(*args, **kwargs) -> _UrlPath:
            result = attr(*args, **kwargs)

            try:
                path = result.as_posix()
            except AttributeError:
                path = str(result)

            return self.with_path(path)

        return wrapper

    def with_scheme(self, scheme: str) -> _UrlPath:
        return self._replace(scheme=scheme)

    def with_netloc(self, netloc: str) -> _UrlPath:
        return self._replace(netloc=netloc)

    def with_path(self, path: str) -> _UrlPath:
        return self._replace(path=path)

    def with_params(self, params: str) -> _UrlPath:
        return self._replace(params=params)

    def with_query(self, query: str) -> _UrlPath:
        return self._replace(query=query)

    def with_fragment(self, fragment: str) -> _UrlPath:
        return self._replace(fragment=fragment)

    def with_port(self, port: int) -> _UrlPath:
        """change the port of the URL or remove it if `port` is `None`"""

        netloc = self.netloc.rsplit(":", 1)[0]

        if port is not None:
            netloc += f":{port:d}"

        return self.with_netloc(netloc)

    def with_hostname(self, hostname: str) -> _UrlPath:
        """change the hostname of the URL"""

        netloc = ""

        if self.username:
            netloc = self.username

            if self.password:
                netloc += f":{self.password}"

            netloc += "@"

        netloc += hostname

        if self.port:
            netloc += f":{self.port}"

        return self.with_netloc(netloc)
