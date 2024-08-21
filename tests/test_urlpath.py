import pytest

from pathlibutil.urlpath import UrlNetloc, UrlPath


@pytest.fixture
def url():
    return UrlPath(
        "hTTps://Foo:Bar@www.ExamplE.com:443/Path/file.txt;params?b=2&a=1#section1"
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
def test_urlpath_with(url, method, attr):

    func = getattr(url, method)

    result = func("")

    assert hasattr(result, attr)


@pytest.mark.parametrize(
    "wrapper",
    [
        "with_suffix",
        "with_name",
        "with_stem",
    ],
)
def test_urlpath_wrapper(url, wrapper, attr):
    func = getattr(url, wrapper)

    result = func(".test")

    assert hasattr(result, attr)


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
