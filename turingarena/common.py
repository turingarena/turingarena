import subprocess

import os
from abc import ABCMeta


class ImmutableObject(metaclass=ABCMeta):
    __slots__ = []

    def __init__(self, **kwargs):
        assert len(kwargs) == len(list(self.all_slots()))
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)

    @classmethod
    def all_slots(cls):
        for base in cls.mro():
            if base == object: continue
            yield from base.__slots__

    def __setattr__(self, key, value):
        raise NotImplementedError

    def __repr__(self):
        args = ", ".join(f"{s}={repr(getattr(self, s, '<MISSING>'))}" for s in self.all_slots())
        return f"{self.__class__.__name__}({args})"


class TupleLikeObject(ImmutableObject):
    __slots__ = []

    def _to_tuple(self):
        return tuple(getattr(self, s) for s in self.__slots__)

    def __eq__(self, other):
        return (
            isinstance(other, TupleLikeObject)
            and self._to_tuple() == other._to_tuple()
        )

    def __hash__(self):
        return hash(self._to_tuple())


def install_with_setuptools(dest_dir, **kwargs):
    def generate_setup_py():
        yield "from setuptools import setup"
        yield
        yield f"setup("
        for kw, arg in kwargs.items():
            yield indent(f"{kw}={repr(arg)},")
        yield f")"

    setup_py_path = os.path.join(
        dest_dir,
        "setup.py",
    )

    with open(setup_py_path, "w") as setup_py_file:
        write_to_file(generate_setup_py(), setup_py_file)

    subprocess.run(
        ["python", "setup.py", "install", "--force"],
        cwd=dest_dir,
    )


def indent_all(lines):
    for line in lines:
        yield indent(line)


def indent(line):
    if line is None:
        return None
    else:
        return "    " + line


def write_to_file(lines, file):
    for line in lines:
        if line is None:
            print("", file=file)
        else:
            print(line, file=file)
