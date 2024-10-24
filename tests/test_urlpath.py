import pathlib

import pytest

from pathlibutil.urlpath import UrlNetloc, UrlPath, normalize, url_from


@pytest.fixture
def urlpath():
    return UrlPath(
        "https://Foo:Bar@www.ExamplE.com:443/Path/file.txt;params?b=2&a=1#section1"
    )


@pytest.fixture(
    params=[
        "_path",
        "_kwargs",
        "_url",
    ]
)
def attr(request):
    return request.param


@pytest.fixture(
    params=[
        ("https://www.ExamplE.com:443", "https://www.example.com"),
        ("http://Foo@www.ExamplE.com:80", "http://Foo@www.example.com"),
        ("http://Foo:baR@www.Example.cOm:8080", "http://Foo:baR@www.example.com:8080"),
        (
            "http://[::FFFF:129.144.52.38]:80/index.html",
            "http://[::ffff:129.144.52.38]/index.html",
        ),
    ],
    ids=lambda x: x[0],
)
def urls(request):
    return request.param


@pytest.fixture(
    params=[
        ("www.ExamplE.com:443", "www.example.com:443"),
        ("Foo@www.ExamplE.com", "Foo@www.example.com"),
        ("Foo:baR@www.Example.cOm:8080", "Foo:baR@www.example.com:8080"),
        (
            "-.~_!$&'()*+,;=:%40:80%2f::::::@eXample.com:80",
            "-.~_!$&'()*+,;=:%40:80%2f::::::@example.com:80",
        ),
    ],
    ids=lambda x: x[0],
)
def netlocs(request):
    return request.param


@pytest.mark.parametrize(
    "method",
    [
        "with_scheme",
        "with_netloc",
        "with_path",
        "with_params",
        "with_query",
        "with_fragment",
        "with_port",
        "with_hostname",
        "with_credentials",
    ],
)
def test_urlpath_with(urlpath, method, attr):

    func = getattr(urlpath, method)

    result = func("")

    assert hasattr(result, attr)


@pytest.mark.parametrize(
    "wrapper",
    [w for w in dir(pathlib.PurePosixPath) if w.startswith("with_")],
)
def test_urlpath_wrapper(urlpath, wrapper, attr):
    func = getattr(urlpath, wrapper)

    result = func(".test")

    assert hasattr(result, attr)


@pytest.mark.parametrize(
    "property",
    [
        "name",
        "suffix",
        "stem",
        "parent",
    ],
)
def test_urlpath_property(urlpath, property):
    assert getattr(urlpath, property)


def test_urlpath_geturl_normalize(urls):
    url, result = urls

    netloc = UrlPath(url)

    assert netloc.geturl(True) == result


def test_urlpath_geturl(urls):
    url, _ = urls

    netloc = UrlPath(url)

    assert netloc.geturl() == url


def test_urlpath_str(urls):

    url, result = urls

    assert str(UrlPath(url)) == result


def test_urlnetloc(netlocs):
    url, _ = netlocs

    netloc = UrlNetloc.from_netloc(url)

    assert str(netloc) == url


def test_urlnetloc_normalize(netlocs):
    url, result = netlocs

    netloc = UrlNetloc.from_netloc(url, normalize=True)

    assert str(netloc) == result


def test_urlnetloc_str():
    hostname = "www.example.com"

    netloc = UrlNetloc(hostname=hostname)

    assert str(netloc) == hostname


def test_urlnetloc_dict():
    data = {
        "hostname": "www.example.com",
        "port": 443,
        "username": "Foo",
        "password": None,
    }

    netloc = UrlNetloc(**data)

    assert netloc.to_dict() == data


def test_urlnetloc_dict_prune():
    data = {
        "hostname": "www.example.com",
        "port": 443,
        "username": "Foo",
        "password": None,
    }

    netloc = UrlNetloc(**data)

    del data["password"]

    assert netloc.to_dict(True) == data


def test_normalize_remove_ports():

    result = normalize("https://www.ExamplE.com:443/Path?b=2&a=1")

    assert result == "https://www.example.com/Path?a=1&b=2"


def test_normalize_with_ports():

    result = normalize("https://www.ExamplE.com:443/Path?b=2&a=1", port=True)

    assert result == "https://www.example.com:443/Path?a=1&b=2"


def test_urlpath_validate(urlpath: UrlPath):

    with pytest.raises(ValueError):
        urlpath.with_hostname("[www.example.com")


@pytest.fixture(
    params=[200, 404],
)
def mock_openurl(request, mocker):
    status = request.param

    mock_response = mocker.Mock()
    mock_response.status = status

    mock = mocker.MagicMock()
    mock.return_value = mock_response
    mock.__enter__.return_value = mock_response

    mocker.patch("urllib.request.urlopen", return_value=mock)

    return status


def test_exists(mock_openurl):
    url = UrlPath("http://example.com/file.txt")

    result = mock_openurl == 200

    assert url.exists() is result


def test_exists_raises(mocker):
    mocker.patch("urllib.request.urlopen", side_effect=Exception)

    url = UrlPath("http://example.com/file.txt")

    with pytest.raises(FileNotFoundError):
        url.exists(errors=True)


def test_exists_notraises(mocker):
    mocker.patch("urllib.request.urlopen", side_effect=Exception)

    url = UrlPath("http://example.com/file.txt")

    assert url.exists(errors=False) is False


def test_with_path_raises():
    url = UrlPath("http://example.com/file.txt")

    with pytest.raises(TypeError):
        url.with_path(1)


def test_getattr_raises():
    url = UrlPath("http://example.com/file.txt")

    with pytest.raises(AttributeError):
        url.__getattr__("not_a_method")


def test_repr():
    url = UrlPath("http://example.com/file.txt")

    assert repr(url) == "UrlPath('http://example.com/file.txt')"


def test_url_from():
    url = url_from("//server/root/path/readme.pdf", "https://www.server.com")

    print(str(url))
    assert str(url) == "https://www.server.com/path/readme.pdf"


def test_anchor():
    url = UrlPath("//server/root/path/readme.pdf")

    assert url.anchor == "//server/root"


def test_with_anchor():
    url = UrlPath("//server/root/path/readme.pdf")

    assert (
        url.with_anchor("//fubar", root=True).__str__()
        == "//fubar/root/path/readme.pdf"
    )


def test_fubar_anchor():
    url = UrlPath("//server/root/path/readme.pdf")

    assert url.with_anchor("//fubar").__str__() == "//fubar/path/readme.pdf"
