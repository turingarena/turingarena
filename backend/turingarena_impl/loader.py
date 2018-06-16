import importlib
import os


def find_package_path(name, default_path=None):
    mod_name, rel_path = split_module(name, default_arg=default_path)

    if mod_name:
        mod = importlib.import_module(mod_name)
        for path in find_package_path_all(mod, rel_path):
            return path
    else:
        if os.path.exists(rel_path):
            return rel_path

    raise FileNotFoundError(f"package file not found: {name}")


def find_package_path_all(mod, rel_path):
    for lookup_path in mod.__path__:
        full_path = os.path.join(lookup_path, rel_path)
        if os.path.exists(full_path):
            yield full_path


def split_module(name, default_arg=None):
    if name:
        mod_name, *rest = name.split(":", 1)
    else:
        mod_name = None
        rest = []

    if rest:
        arg = rest[0]
    else:
        arg = default_arg

    return mod_name, arg
