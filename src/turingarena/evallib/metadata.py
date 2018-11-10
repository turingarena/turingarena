import os
from functools import lru_cache

import toml


@lru_cache(None)
def load_metadata(dirpath="."):
    try:
        with open(os.path.join(dirpath, "turingarena.toml")) as f:
            return toml.load(f)
    except FileNotFoundError:
        return {}
