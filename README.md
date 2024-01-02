# pathlibutil

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pathlibutil)](https://pypi.org/project/pathlibutil/)
[![PyPI](https://img.shields.io/pypi/v/pathlibutil)](https://pypi.org/project/pathlibutil/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pathlibutil)](https://pypi.org/project/pathlibutil/)
[![PyPI - License](https://img.shields.io/pypi/l/pathlibutil)](./LICENSE)
[![GitHub Workflow Test)](https://img.shields.io/github/actions/workflow/status/d-chris/pathlibutil/pytest.yml?logo=github&label=pytest)](https://github.com/d-chris/pathlibutil/actions/workflows/pytest.yml)

---

`pathlibutil.Path` inherits from  `pathlib.Path` with some useful built-in python functions.

- `Path().hexdigest()` to calculate and `Path().verify()` for verification of hexdigest from a file
- `Path.default_hash` to configurate default hash algorithm for `Path` class (default: *'md5'*)
- `Path().size()` to get size in bytes of a file or directory
- `Path().read_lines()` to yield over all lines from a file until EOF
- `contextmanager` to change current working directory with `with` statement
- `Path().copy()` copy a file or directory to a new path destination
- `Path().delete()` delete a file or directory-tree
  
## Installation

```bash
pip install pathlibutil
```

## Usage

```python
from pathlibutil import Path

readme = Path('README.md')

print(f'File size: {readme.size()} Bytes')
print(f'File sha1: {readme.hexdigest("sha1")}')

print('-- File content --')
for line in readme.read_lines(encoding='utf-8'):
    print(line, end='')
print('-- EOF --')

with readme.parent as cwd:
    print(f'Current working directory: {cwd}')

# Change default hash algorithm from md5 to sha1
Path.default_hash = 'sha1'

print(f'File verification: {readme.verify("add3f48fded5e0829a8e3e025e44c2891542c58e")}')
```

## Examples

1. [Read file line by line to stdout](./examples/example1.py)
   > `Path().read_lines()`
2. [Write calculated hash to file](./examples/example2.py)
   > `Path().hexdigest()`
3. [Read hashes from file for verification](./examples/example3.py)
   > `Path().verify()` and `contextmanager`
