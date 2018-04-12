import importlib
import os
import types

from future.moves import sys


def make_dummy_package(name, path):
    """
    Creates a dummy python package with a given path,
    used for looking for submodules and turingarena data.
    """
    mod = types.ModuleType(name)
    mod.__package__ = mod.__name__
    mod.__path__ = path
    sys.modules[name] = mod
    return mod


base_problem_module = make_dummy_package("__turingarena_base__", [""])


def find_package_path(mod, rel_path):
    for path in find_package_path_all(mod, rel_path):
        return path
    raise FileNotFoundError(f"package file not found: {mod.__name__}:{rel_path}")


def find_package_path_all(mod, rel_path):
    for lookup_path in mod.__path__:
        full_path = os.path.join(lookup_path, rel_path)
        if os.path.exists(full_path):
            yield full_path


def split_module(name, *, default_arg=None):
    if name:
        mod_name, *rest = name.split(":", 1)
    else:
        mod_name = None
        rest = []

    if mod_name:
        mod = importlib.import_module(mod_name)
    else:
        mod = base_problem_module

    if rest:
        arg = rest[0]
    else:
        arg = default_arg
    return mod, arg
