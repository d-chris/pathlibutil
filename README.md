<!--
filename: ./README.md
-->

# pathlibutil

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pathlibutil)](https://pypi.org/project/pathlibutil/)
[![PyPI - Version](https://img.shields.io/pypi/v/pathlibutil)](https://pypi.org/project/pathlibutil/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pathlibutil)](https://pypi.org/project/pathlibutil/)
[![PyPI - License](https://img.shields.io/pypi/l/pathlibutil)](https://raw.githubusercontent.com/d-chris/pathlibutil/main/LICENSE)
[![GitHub - Pytest](https://img.shields.io/github/actions/workflow/status/d-chris/pathlibutil/pytest.yml?logo=github&label=pytest)](https://github.com/d-chris/pathlibutil/actions/workflows/pytest.yml)
[![GitHub - Page](https://img.shields.io/website?url=https%3A%2F%2Fd-chris.github.io%2Fpathlibutil&up_message=pdoc&logo=github&label=documentation)](https://d-chris.github.io/pathlibutil)
[![GitHub - Release](https://img.shields.io/github/v/tag/d-chris/pathlibutil?logo=github&label=github)](https://github.com/d-chris/pathlibutil)
[![codecov](https://codecov.io/gh/d-chris/pathlibutil/graph/badge.svg?token=U7I9FYMRSR)](https://codecov.io/gh/d-chris/pathlibutil)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://raw.githubusercontent.com/d-chris/pathlibutil/main/.pre-commit-config.yaml)

---

`pathlibutil.Path` inherits from  `pathlib.Path` with some useful built-in python functions from `shutil` and `hashlib`

- `Path.hexdigest()` to calculate and `Path.verify()` for verification of hexdigest from a file
- `Path.default_hash` to configurate default hash algorithm for `Path` class (default: *'md5'*)
- `Path.size()` to get size in bytes of a file or directory
  - `byteint` function decorator converts the return value of `int` to a `ByteInt` object
- `Path.read_lines()` to yield over all lines from a file until EOF
- `contextmanager` to change current working directory with `with` statement
- `Path.copy()` copy a file or directory to a new path destination
- `Path.delete()` delete a file or directory-tree
- `Path.move()` move a file or directory to a new path destination
- `Path.make_archive()` creates and `Path.unpack_archive()` uncompresses an archive from a file or directory
- `Path.archive_formats` to get all available archive formats
- `Path.stat()` returns a `StatResult` object to get file or directory information containing
  - `TimeInt` objects for `atime`, `ctime`, `mtime` and `birthtime`
  - `ByteInt` object for `size`
- `Path.relative_to()` to get relative path from a file or directory, `walk_up` to walk up the directory tree.
- `Path.with_suffix()` to change the multiple suffixes of a file
- `Path.cwd()` to get the current working directory or executable path when script is bundled, e.g. with `pyinstaller`
- `Path.resolve()` to resolve a unc path to a mapped windows drive.
- `Path.walk()` to walk over a directory tree like `os.walk()`
- `Path.iterdir()` with `recursive` all files from the directory tree will be yielded and `exclude_dirs` via callable.
- `Path.is_expired()` to check if a file is expired by a given `datetime.timedelta`
- `Path.expand()` yields file paths for multiple file patterns if they exsits.

JSON serialization of `Path` objects is supported in `pathlibutil.json`.

- `pathlibutil.json.dumps()` and `pathlibutil.json.dump()` to serialize `Path` objects as posix paths.

Parse and modify URLs with `pathlibutil.urlpath`.

- `pathlibutil.urlpath.UrlPath()` modify URL and easy access the `path` of the url like a `pathlib.PurePosixPath` object.
- `pathlibutil.urlpath.UrlNetloc()` to parse and modify the `netloc` part of a URL.
- `pathlibutil.urlpath.normalize()` to normalize a URL string.
- `pathlibutil.urlpath.url_from()` to create a URL from an UNC path object.


## Installation

```bash
pip install pathlibutil
```

### 7zip support

to handle 7zip archives, an extra package `py7zr>=0.20.2` is required!

[![PyPI - Version](https://img.shields.io/pypi/v/py7zr?logo=python&logoColor=white&label=py7zr&color=FFFF33)](https://pypi.org/project/py7zr/)

```bash
# install as extra dependency
pip install pathlibutil[7z]
```

## Usage

```python
from pathlibutil import Path

readme = Path('README.md')

print(f'File size: {readme.size()} Bytes')
```

## Example 1

Read a file and print its content and some file information to stdout.
> `Path.read_lines()`

```python
from pathlibutil import Path

readme = Path("README.md")

print(f"File size: {readme.size()} Bytes")
print(f'File sha1: {readme.hexdigest("sha1")}')

print("File content".center(80, "="))

for line in readme.read_lines(encoding="utf-8"):
  print(line, end="")

print("EOF".center(80, "="))
```

## Example 2

Write a file with md5 checksums of all python files in the pathlibutil-directory.
> `Path.hexdigest()`

```python
from pathlibutil import Path

file = Path("pathlibutil.md5")

with file.open("w") as f:
  f.write(
      "# MD5 checksums generated with pathlibutil "
      "(https://pypi.org/project/pathlibutil/)\n\n"
  )

  i = 0
  for i, filename in enumerate(Path("./pathlibutil").glob("*.py"), start=1):
    f.write(f"{filename.hexdigest()} *{filename}\n")

print(f"\nwritten: {i:>5} {file.default_hash}-hashes to: {file}")
```

## Example 3

Read a file with md5 checksums and verify them.
> `Path.verify()`, `Path.default_hash` and `contextmanager`

```python
from pathlibutil import Path

file = Path("pathlibutil.md5")


def no_comment(line: str) -> bool:
  return not line.startswith("#")


with file.parent as cwd:
  miss = 0
  ok = 0
  fail = 0

  for line in filter(no_comment, file.read_lines()):
    try:
      digest, filename = line.strip().split(" *")
      verification = Path(filename).verify(digest, "md5")
    except ValueError as split_failed:
      continue
    except FileNotFoundError as verify_failed:
      tag = "missing"
      miss += 1
    else:
      if verification:
        tag = "ok"
        ok += 1
      else:
        tag = "fail"
        fail += 1

    print(f'{tag.ljust(len(digest), ".")} *{filename}')

  print(f"\nok: {ok:<5} fail: {fail:<5} missing: {miss}")
```

## Example 4

Search all pycache directories and free the memory and display the number of
deleted directories and the amount of memory freed in MB.
> `Path.delete()`, `Path.size()` and `ByteInt`

```python
from pathlibutil import ByteInt, Path

mem = ByteInt(0)
i = 0

for i, cache in enumerate(Path(".").rglob("*/__pycache__/"), start=1):
  cache_size = cache.size()
  try:
    cache.delete(recursive=True)
  except OSError:
    print(f"Failed to delete {cache}")
  else:
    mem += cache_size

print(f"{i} cache directories deleted, {mem:.1mb} MB freed.")
```

## Example 5

Inherit from `pathlibutil.Path` to register new a archive format. Specify a
`archive` as keyword argument in the new subclass, which has to be the suffix
without `.` of the archives. Implement a classmethod `_register_archive_format()`
to register new archive formats.

> Path.make_archive(), Path.archive_formats and Path.move()

```python
import shutil

import pathlibutil


class RegisterFooBarFormat(pathlibutil.Path, archive="foobar"):
  @classmethod
  def _register_archive_format(cls):
    """
    implement new register functions for given `archive`
    """
    try:
      import required_package_name
    except ModuleNotFoundError:
      raise ModuleNotFoundError("pip install <required_package_name>")

    def pack_foobar(
        base_name, base_dir, owner=None, group=None, dry_run=None, logger=None
    ) -> str:
      """callable that will be used to unpack archives.

      Args:
          base_name (`str`): name of the file to create
          base_dir (`str`): directory to start archiving from, defaults to `os.curdir`
          owner (`Any`, optional): as passed in `make_archive(*args, owner=None, **kwargs)`. Defaults to None.
          group (`Any`, optional): as passed in `make_archive(*args, group=None, **kwargs)`. Defaults to None.
          dry_run (`Any`, optional): as passed in `make_archive(*args, dry_run=None, **kwargs)`. Defaults to None.
          logger (`logging.Logger`, optional): as passed in `make_archive(*args, logger=None, **kwargs)`. Defaults to None.

      Returns:
          str: path of the new created archive
      """
      raise NotImplementedError("implement your own pack function")

    def unpack_foobar(archive, path, filter=None, extra_args=None) -> None:
      """callable that will be used to unpack archives.

      Args:
          archive (`str`): path of the archive
          path (`str`): directory the archive must be extracted to
          filter (`Any`, optional): as passed in `unpack_archive(*args, filter=None, **kwargs)`. Defaults to None.
          extra_args (`Sequence[Tuple[name, value]]`, optional): additional keyword arguments, specified by `register_unpack_format(*args, extra_args=None, **kwargs)`. Defaults to None.
      """
      raise NotImplementedError("implement your own unpack function")

    shutil.register_archive_format(
        "foobar", pack_foobar, description="foobar archives"
    )
    shutil.register_unpack_format("foobar", [".foo.bar"], unpack_foobar)


file = pathlibutil.Path("README.md")

print(f"available archive formats: {file.archive_formats}")

archive = file.make_archive("README.foo.bar")

backup = archive.move("./backup/")

print(f"archive created: {archive.name} and moved to: {backup.parent}")
```

## Example 6

Access the current working directory with optional parameter `frozen` to determine
different directories when script is bundled to an executable,
e.g. with `pyinstaller`.
> `Path.cwd()`

```cmd
>>> poetry run examples/example6.py -b
Building frozen: K:/pathlibutil/examples/example6.exe
Build succeeded: 0

>>> poetry run examples/example6.py
we are                          not frozen

bundle dir is                   K:/pathlibutil/examples
sys.argv[0] is                  K:/pathlibutil/examples/example6.py
sys.executable is               K:/pathlibutil/.venv/Scripts/python.exe
os.getcwd is                    K:/pathlibutil

Path.cwd(frozen=True) is        K:/pathlibutil
Path.cwd(frozen=False) is       K:/pathlibutil
Path.cwd(frozen=_MEIPASS) is    K:/pathlibutil

>>> examples/example6.exe
we are                          ever so frozen

bundle dir is                   C:/Users/CHRIST~1.DOE/AppData/Local/Temp/_MEI106042
sys.argv[0] is                  examples/example6.exe
sys.executable is               K:/pathlibutil/examples/example6.exe
os.getcwd is                    K:/pathlibutil

Path.cwd(frozen=True) is        K:/pathlibutil/examples
Path.cwd(frozen=False) is       K:/pathlibutil
Path.cwd(frozen=_MEIPASS) is    C:/Users/CHRIST~1.DOE/AppData/Local/Temp/_MEI106042
```

## Example 7

Console application to convert UNC paths to intranet URLs.

By default, it checks if the filename and URL are available and copies the
normalized URL to the clipboard.

> `pathlibutil.urlpath.url_from()`

```python
import argparse
import sys

try:
    import pyperclip

    import pathlibutil.urlpath as up
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(f"pip install {e.name.split('.')[0]}") from e


def intranet_from(uncpath: str, check: bool = True) -> str:
    """
    Return the intranet URL for the given UNC path.
    """

    url = up.url_from(
        uncpath,
        hostname="http://intranet.example.de",
        strict=check,
    )

    return url.normalize()


def cli():

    parser = argparse.ArgumentParser(
        description=intranet_from.__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "filename",
        nargs="*",
        help="The UNC path to the file.",
    )
    parser.add_argument(
        "-c",
        "--no-check",
        action="store_false",
        dest="check",
        help="Don't check if filename and url is available.",
    )
    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="Do not print the url to stdout.",
    )
    parser.add_argument(
        "-n",
        "--no-clip",
        action="store_false",
        dest="clip",
        help="Don't copy the url to the clipboard.",
    )

    args = parser.parse_args()
    filename = " ".join(args.filename)

    url = intranet_from(filename, check=args.check)

    if not args.silent:
        print(url)

    if args.clip:
        pyperclip.copy(url)


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
```
