import os
from functools import lru_cache

import toml


METADATA_FILE_NAMES = ["Turingfile", "turingarena.toml"]


@lru_cache(None)
def load_metadata(dirpath="."):
    for name in METADATA_FILE_NAMES:
        try:
            with open(os.path.join(dirpath, name)) as f:
                return toml.load(f)
        except FileNotFoundError:
            continue
    return {}

