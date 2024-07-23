"""
Wrapper around the `json` module that provides a custom JSON encoder for `pathlib.Path`
objects. This allows `pathlib.Path` objects to be serialized to JSON without having to
convert them to strings first.

```python
from pathlib import Path
from pathlibutil.json import dump

data = {"file": Path(__file__)}

with open("data.json", "w") as f:
    dump(data, f)
```
"""

import functools
import json
import pathlib
from json import load, loads


class PathEncoder(json.JSONEncoder):
    """
    JSON encoder that converts `pathlib.Path` objects to their string representation.
    """

    def default(self, obj):
        """
        Convert `pathlib.Path` objects to a string using `pathlib.Path.as_posix()`.
        """
        if isinstance(obj, pathlib.Path):
            return obj.as_posix()

        return super().default(obj)


@functools.wraps(json.dump)
def dump(obj, fp, *, cls=PathEncoder, **kwargs):
    return json.dump(obj, fp, cls=cls, **kwargs)


@functools.wraps(json.dumps)
def dumps(obj, *, cls=PathEncoder, **kwargs):
    return json.dumps(obj, cls=cls, **kwargs)


__all__ = ["load", "loads", "dump", "dumps", "PathEncoder"]
