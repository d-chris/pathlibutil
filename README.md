# pathlibutil

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pathlibutil)](https://pypi.org/project/pathlibutil/)
[![PyPI](https://img.shields.io/pypi/v/pathlibutil)](https://pypi.org/project/pathlibutil/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pathlibutil)](https://pypi.org/project/pathlibutil/)
[![PyPI - License](https://img.shields.io/pypi/l/pathlibutil)](https://raw.githubusercontent.com/d-chris/pathlibutil/main/LICENSE)
[![GitHub Workflow Test)](https://img.shields.io/github/actions/workflow/status/d-chris/pathlibutil/pytest.yml?logo=github&label=pytest)](https://github.com/d-chris/pathlibutil/actions/workflows/pytest.yml)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fd-chris.github.io%2Fpathlibutil&up_message=pdoc&logo=github&label=documentation)](https://d-chris.github.io/pathlibutil)
[![GitHub tag (with filter)](https://img.shields.io/github/v/tag/d-chris/pathlibutil?logo=github&label=github)](https://github.com/d-chris/pathlibutil)

---

`pathlibutil.Path` inherits from  `pathlib.Path` with some useful built-in python functions.

- `Path().hexdigest()` to calculate and `Path().verify()` for verification of hexdigest from a file
- `Path.default_hash` to configurate default hash algorithm for `Path` class (default: *'md5'*)
- `Path().size()` to get size in bytes of a file or directory
- `Path().read_lines()` to yield over all lines from a file until EOF
- `contextmanager` to change current working directory with `with` statement
- `Path().copy()` copy a file or directory to a new path destination
- `Path().delete()` delete a file or directory-tree
- `Path().move()` move a file or directory to a new path destination
  
## Installation

```bash
pip install pathlibutil
```

## Usage

```python
from pathlibutil import Path

readme = Path('README.md')

print(f'File size: {readme.size()} Bytes')
```

## Example 1

Read a file and print its content and some file information to stdout.
> `Path().read_lines()`

```python
readme = Path('README.md')

print('File content'.center(80, '='))

for line in readme.read_lines(encoding='utf-8'):
   print(line, end='')

print('EOF'.center(80, '='))
```

## Example 2

Write a file with md5 checksums of all python files in the pathlibutil-directory.
> `Path().hexdigest()`

```python
file = Path('pathlibutil.md5')

algorithm = file.suffix[1:]

with file.open('w') as f:
   f.write(
      f'# {algorithm} checksums generated with pathlibutil (https://pypi.org/project/pathlibutil/)\n\n')

   i = 0
   for i, filename in enumerate(Path('./pathlibutil').glob('*.py'), start=1):
      f.write(f'{filename.hexdigest(algorithm)} *{filename}\n')

print(f'\nwritten: {i:>5} {algorithm}-hashes to: {file}')
```

## Example 3

Read a file with md5 checksums and verify them.
> `Path().verify()`, `Path.default_hash` and `contextmanager`

```python
file = Path('pathlibutil.md5')

Path.default_hash = file.suffix[1:]

def no_comment(line: str) -> bool:
   return not line.startswith('#')

with file.parent as cwd:

   for line in filter(no_comment, file.read_lines()):
      try:
            digest, filename = line.strip().split(' *')
            verification = Path(filename).verify(digest)
      except ValueError as split_failed:
            continue
      except FileNotFoundError as verify_failed:
            tag = 'missing'
      else:
            tag = 'ok' if verification else 'fail

      print(f'{tag.ljust(len(digest), ".")} *{filename}')
```

## Example 4

Search all pycache directories and free the memory.
> `Path().delete()` and `Path().size()`

```python
mem = 0
i = 0

for i, cache in enumerate(Path('.').rglob('*/__pycache__/'), start=1):
      cache_size = cache.size()
      try:
            cache.delete(recursive=True)
      except OSError:
            print(f'Failed to delete {cache}')
      else:
            mem += cache_size

print(f'{i} cache directories deleted, {mem / 2**20:.2f} MB freed.')
```
