import os

import toml


def load_metadata(dirpath="."):
    try:
        with open(os.path.join(dirpath, "turingarena.toml")) as f:
            return toml.load(f)
    except FileNotFoundError:
        return {}
