import functools
import importlib
import os
import pathlib

json = importlib.import_module("json")

from json import load, loads


class PathEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pathlib.Path):
            return obj.as_posix()

        return super().default(obj)


@functools.wraps(json.dump)
def dump(obj, fp, *, cls=PathEncoder, **kwargs):
    return json.dump(obj, fp, cls=cls, **kwargs)


@functools.wraps(json.dumps)
def dumps(obj, *, cls=PathEncoder, **kwargs):
    return json.dumps(obj, cls=cls, **kwargs)
