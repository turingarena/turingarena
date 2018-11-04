import os

import sys


def find_package_file(file_path, lookup_paths=None):
    if lookup_paths is None:
        lookup_paths = sys.path + [os.getcwd()]
    for path in find_package_files(file_path, lookup_paths):
        return path
    raise FileNotFoundError(f"package file not found: {file_path}")


def find_package_files(file_path, lookup_paths):
    if os.path.isabs(file_path):
        if os.path.exists(file_path):
            yield file_path
    else:
        for lookup_path in lookup_paths:
            full_path = os.path.join(lookup_path, file_path)
            if os.path.exists(full_path):
                yield full_path
