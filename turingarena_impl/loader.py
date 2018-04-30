import importlib
import importlib.util
import os


def find_package_path(mod, rel_path):
    if not mod:
        if os.path.exists(rel_path):
            return rel_path
    else:
        for path in find_package_path_all(mod, rel_path):
            return path
    raise FileNotFoundError(f"package file not found: {mod}:{rel_path}")


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
        mod = None

    if rest:
        arg = rest[0]
    else:
        arg = default_arg
    return mod, arg
