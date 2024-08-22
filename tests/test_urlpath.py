import pathlib

import pytest

from pathlibutil.urlpath import UrlNetloc, UrlPath, normalize_url


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


def test_normalize_url_remove_ports():

    result = normalize_url("https://www.ExamplE.com:443/Path?b=2&a=1")

    assert result == "https://www.example.com/Path?a=1&b=2"


def test_normalize_url_with_ports():

    result = normalize_url("https://www.ExamplE.com:443/Path?b=2&a=1", port=True)

    assert result == "https://www.example.com:443/Path?a=1&b=2"


def test_urlpath_validate(urlpath: UrlPath):

    with pytest.raises(ValueError):
        urlpath.with_hostname("[www.example.com")
