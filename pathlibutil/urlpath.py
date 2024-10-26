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

    Attributes:
        hostname (str): The hostname of the URL.
        port (Optional[int]): The port number of the URL. Defaults to None.
        username (Optional[str]): The username for authentication. Defaults to None.
        password (Optional[str]): The password for authentication. Defaults to None.

    Examples:
        >>> url = UrlNetloc.from_netloc("www.example.com:443")
        >>> url.port = None
        >>> str(url)
        'www.example.com'
    """

    hostname: str
    """
    The hostname of the URL.

    Examples:
        'www.example.com'
    """
    port: Optional[int] = field(default=None)
    """
    The port number of the URL. Defaults to None.
    """
    username: Optional[str] = field(default=None)
    """
    The username for authentication. Defaults to None
    """
    password: Optional[str] = field(default=None)
    """
    The password for authentication. Defaults to None.
    """

    def __str__(self) -> str:
        return self.netloc

    @property
    def netloc(self) -> str:
        """
        Return the netloc string representation of the `dataclass`.

        Returns:
            str: The netloc string representation.

        Examples:
            >>> UrlNetloc("www.example.de", 433, "user", "pass").netloc
            'user:pass@www.example.de:433'
        """

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
        """
        Parse a netloc string into a `UrlNetloc` object.

        Args:
            netloc (str): The netloc string to parse.

        Returns:
            `UrlNetloc`: An instance of `UrlNetloc` with the parsed components.

        Examples:
            >>> UrlNetloc.from_netloc("user:pass@example.de:433")
            UrlNetloc(hostname='example.de', port=433, username='user', password='pass')
        """

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
        Convert the `UrlNetloc` object to a dictionary.

        Args:
            prune (bool): If True, removes key-value pairs where the value is `None`.
                Defaults to False.

        Returns:
            dict: A dictionary representation of the `UrlNetloc` object.

        Examples:
            >>> loc = UrlNetloc("example.de", 80, "user")

            >>> loc.to_dict()
            {'hostname': 'example.de', 'port': 80, 'username': 'user', 'password': None}

            >>> loc.to_dict(prune=True)
            {'hostname': 'www.example.de', 'port': 80, 'username': 'user'}
        """

        data = asdict(self)

        if not prune:
            return data

        return {k: v for k, v in data.items() if v is not None}


_UrlPath = TypeVar("_UrlPath", bound="UrlPath")


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

    This class wraps `pathlib.PurePosixPath` methods to return a new `UrlPath` object.
    Attributes and methods from `PurePosixPath`, such as `name` and `with_suffix`,
    are available.

    Examples:
        >>> url = UrlPath("https://www.example.com/path/file.txt")

        >>> url.name
        'file.txt'

        >>> url.with_suffix(".html")
        UrlPath('https://www.example.com/path/file.html')
    """

    _default_ports = {
        "http": 80,
        "https": 443,
    }

    def __new__(cls, url, **kwargs) -> _UrlPath:
        url = (
            f"//{url[1:]}" if url.startswith("/") and not url.startswith("//") else url
        )

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

        Args:
            url (str): The URL string to initialize the `UrlPath` object.
            scheme (str, optional): The scheme to use if not present in the URL.
                Defaults to an empty string.
            allow_fragments (bool, optional): Whether to allow fragments in the URL.
                Defaults to True.

        Raises:
            ValueError: If the URL is not valid.

        Examples:
            >>> UrlPath("http://example.com/path/file.txt")
            UrlPath('http://example.com/path/file.txt')
        """
        self._url = url
        self._kwargs = {
            "scheme": scheme,
            "allow_fragments": allow_fragments,
        }
        self._path = pathlib.PurePosixPath(up.unquote(self.path))

    def __str__(self) -> str:
        return self.normalize()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.geturl()!r})"

    def geturl(self, normalize: bool = False) -> str:
        """
        Return a re-combined version of the URL.

        If `normalize` is `True`, the scheme and netloc are converted to lowercase,
        default ports are removed, and query parameters are sorted.

        Args:
            normalize (bool): If True, normalizes the URL. Defaults to False.

        Returns:
            str: The re-combined URL.

        Examples:
            >>> url = UrlPath("HTTP://Example.COM:80/path/file name.txt?b=2&a=1")

            >>> url.geturl(normalize=True)
            'http://example.com/path/file%20name.txt?a=1&b=2'

            >>> url.geturl()
            'http://Example.COM:80/path/file name.txt?b=2&a=1'
        """
        if normalize:
            return self.normalize()

        return super().geturl()

    def normalize(self, sort: bool = True, **kwargs) -> str:
        """
        Normalize the URL by converting the scheme and host to lowercase, removing the
        default port if present, and sorting the query parameters.

        Args:
            sort (bool): If True, sorts the query parameters. Defaults to True.
            **kwargs: Additional arguments, such as custom port mappings.

        Returns:
            str: The normalized URL.

        Examples:
            >>> url = UrlPath("HTTP://Example.COM:80/path/file name.txt?b=2&a=1")
            >>> url.normalize()
            'http://example.com/path/file%20name.txt?a=1&b=2'
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
        Add or Change the `UrlPath.scheme` of the URL.

        Args:
            scheme (str): The new scheme to set in the URL.

        Returns:
            `UrlPath`: A new URL with the updated scheme.

        Examples:
            >>> url = UrlPath("http://example.com/path/file.txt")
            >>> url.with_port(990).with_scheme("ftp")
            UrlPath('ftp://example.com:990/path/file.txt')
        """
        return self._replace(scheme=scheme)

    @urlpath
    def with_netloc(self, netloc: Union[str, UrlNetloc]) -> _UrlPath:
        """
        Add or Change the `UrlPath.netloc` of the URL.

        Args:
            netloc (Union[str, UrlNetloc]): The new netloc to set in the URL. It can be
                a string or an instance of `UrlNetloc`.

        Returns:
            `UrlPath`: A new URL with the updated netloc.

        Examples:
            >>> url = UrlPath("http://www.oldhost.com/path/file.txt")
            >>> url.with_netloc("example.com")
            UrlPath('http://example.com/path/file.txt')
        """
        return self._replace(netloc=str(netloc))

    @urlpath
    def with_path(self, path: Union[str, pathlib.PurePosixPath]) -> _UrlPath:
        """
        Add or Change the `UrlPath.path` of the URL.

        Args:
            path (Union[str, pathlib.PurePosixPath]): The new path to set in the URL.

        Returns:
            `UrlPath`: A new URL with the updated path.

        Raises:
            TypeError: If the provided path is of the wrong type

        Examples:
            >>> url = UrlPath("http://example.com/oldpath")
            >>> url.with_path("/path/file.txt")
            UrlPath('http://example.com/path/file.txt')
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
        Change the `UrlPath.params` of the URL.

        Args:
            params (str): The new parameters to set in the URL.

        Returns:
            `UrlPath`: A new URL with the updated parameters.

        Examples:
            >>> url = UrlPath("http://example.com/path")
            >>> url.with_params("param1=value1;param2=value2")
            UrlPath('http://example.com/path;param1=value1;param2=value2')
        """
        return self._replace(params=params)

    @urlpath
    def with_query(self, query: str) -> _UrlPath:
        """
        Add or Change the `UrlPath.query` of the URL.

        Args:
            query (str): The new query string to set in the URL.

        Returns:
            `UrlPath`: A new URL with the updated query string.

        Examples:
            >>> url = UrlPath("http://example.com/path")
            >>> url.with_query("key=value")
            UrlPath('http://example.com/path?key=value')
        """
        return self._replace(query=query)

    @urlpath
    def with_fragment(self, fragment: str) -> _UrlPath:
        """
        Add or Change the `UrlPath.fragment` of the URL.

        Args:
            fragment (str): The new fragment to set in the URL.

        Returns:
            `UrlPath`: A new URL with the updated fragment.

        Examples:
            >>> url = UrlPath("http://example.com/path")
            >>> url.with_fragment("section1")
            UrlPath('http://example.com/path#section1')
        """
        return self._replace(fragment=fragment)

    def with_port(self, port: int) -> _UrlPath:
        """
        Add or Change the `UrlPath.port` in the netloc of the URL.

        If `port` is `None`, the port is removed.

        Args:
            port (int): The new port to set in the URL.

        Returns:
            `UrlPath`: A new URL with the updated port.

        Examples:
            >>> url = UrlPath("http://example.de/path/file.txt")
            >>> url.with_port(8080)
            UrlPath('http://example.de:8080/path/file.txt')
        """

        netloc = UrlNetloc.from_netloc(self.netloc)
        netloc.port = port

        return self.with_netloc(netloc)

    def with_hostname(self, hostname: str) -> _UrlPath:
        """
        Change the `UrlPath.hostname` in the netloc of the URL.

        Args:
            hostname (str): The new hostname to set in the URL.

        Returns:
            `UrlPath`: A new URL with the updated hostname.

        Examples:
            >>> url = UrlPath("http://example.de/path/file.txt")
            >>> url.with_hostname("www.server.com")
            UrlPath('http://www.server.com/path/file.txt')
        """

        netloc = UrlNetloc.from_netloc(self.netloc)
        netloc.hostname = hostname

        return self.with_netloc(netloc)

    def with_credentials(self, username: str, password: str = None) -> _UrlPath:
        """
        Add or change the username and password in the netloc of the URL.

        To change only `username`, the `password` must also be provided.
        If `username` is `None`, the credentials are removed.

        Args:
            username (str): The new username to set in the URL.
            password (str, optional): The new password to set in the URL.
                Defaults to None.

        Returns:
            `UrlPath`: A new URL with the updated credentials.

        Examples:
            >>> url = UrlPath("ftp://example.com/path")
            >>> url.with_credentials("user", "pass")
            UrlPath('ftp://user:pass@example.com/path')
        """

        netloc = UrlNetloc.from_netloc(self.netloc)
        netloc.username = username
        netloc.password = password

        return self.with_netloc(netloc)

    @cached_property
    def parts(self) -> Tuple[str, ...]:
        """
        Returns the parts of the path without any leading '/'.

        Returns:
            Tuple[str, ...]: A tuple containing the parts of the path.

        Examples:
            >>> UrlPath("//server/root/path/file.txt").parts
            ('root', 'path', 'file.txt')
        """
        return tuple(part for part in self._path.parts if not part.startswith("/"))

    @property
    def anchor(self) -> str:
        """
        Concatenates the netloc and root of the path.

        Returns:
            str: The combined netloc and root of the path.

        Examples:
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
        Change the `UrlPath.anchor` of the URL.

        If `root` is `True`, the root of the path will not be removed.

        Args:
            anchor (str): The new anchor to set for the URL.
            root (bool): If `True`, the root of the path will not be removed.
                Defaults to `False`.
            **kwargs: Additional arguments to pass to the UrlPath class constructor.

        Returns:
            `UrlPath`: A new URL with the updated anchor.

        Examples:
            >>> url = UrlPath("//server/root/path/file.txt")

            >>> url.with_anchor("https://www.server.com")
            UrlPath('https://www.server.com/path/file.txt')

            >>> url.with_anchor("https://www.server.com", root=True)
            UrlPath('https://www.server.com/root/path/file.txt')
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
        Check if the URL exists by making an HTTP request.

        Args:
            errors (bool): If True, raises a FileNotFoundError when the URL does
                not exist. Defaults to False.
            **kwargs: Additional arguments to pass to `urllib.request.urlopen`.

        Returns:
            bool: True if the URL exists (HTTP status 200), False otherwise.

        Raises:
            FileNotFoundError: If `errors` is True and the URL does not exist.
        """
        url = self.normalize()

        try:
            with urllib.request.urlopen(url, **kwargs) as response:
                return response.status == 200
        except Exception as e:
            if errors is not False:
                raise FileNotFoundError(url) from e

        return False


def url_from(
    uncpath: str,
    hostname: str,
    *,
    strict: bool = False,
    **kwargs,
) -> UrlPath:
    """
    Convert a UNC path to an URL.

    Args:
        uncpath (str): The UNC path to convert.
        hostname (str): The hostname to replace server and root from the UNC path.
        strict (bool, optional): Check if the uncpath and URL exists.
            Defaults to False.
        **kwargs: Additional keyword arguments for `UrlPath.with_anchor()`.

    Returns:
        UrlPath: The converted URL.

    Raises:
        FileNotFoundError: If uncpath or URL does not exits and strict is True.

    Examples:
        >>> url_from(r"\\\\server\\root\\path\\readme.pdf", "https://www.server.com")
        UrlPath('https://www.server.com/path/readme.pdf')
    """
    filename = pathlib.Path(uncpath).resolve(strict=strict)

    url: UrlPath = UrlPath(filename.as_posix()).with_anchor(hostname, **kwargs)

    if strict:
        url.exists(errors=True)

    return url


def normalize(
    url: str,
    port: bool = False,
    sort: bool = True,
) -> str:
    """
    Normalize a URL by converting the scheme and host to lowercase, optionally removing
    the port, and sorting the query parameters.

    Args:
        url (str): The URL to normalize.
        port (bool, optional): If False, remove the port from the URL.
            Defaults to False.
        sort (bool, optional): If True, sort the query parameters. Defaults to True.

    Returns:
        str: The normalized URL.

    Examples:
        >>> normalize("https://www.ExamplE.com:443/Path?b=2&a=1")
        'https://www.example.com/Path?a=1&b=2'
    """

    url: UrlPath = UrlPath(url)

    if port is False:
        ports = {url.scheme.lower(): url.port}
    else:
        ports = {}

    return url.normalize(sort=sort, ports=ports)


def normalize_url(*args, **kwargs) -> str:
    """
    Deprecated function, use `pathlibutil.urlpath.normalize()` instead.

    Will be removed in the future.
    """

    import warnings

    warnings.warn(
        "normalize_url() is deprecated, use normalize() instead.\n"
        + "Will be removed in the future.",
        DeprecationWarning,
        stacklevel=2,
    )

    return normalize(*args, **kwargs)


__all__ = [
    "UrlNetloc",
    "UrlPath",
    "normalize",
    "url_from",
]
