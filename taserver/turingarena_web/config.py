import os
import toml

DEFAULT_CONFIG_PATHS = [
    "/usr/local/etc/turingarena.conf",
    "/etc/turingarena.conf",
    "./etc/turingarena.conf",
    "./turingarena.conf"
]


def find_config_path():
    path = os.getenv("TA_CONFIG_FILE")
    if path is not None and os.path.exists(path):
        return path
    for path in DEFAULT_CONFIG_PATHS:
        if os.path.exists(path):
            return path
    raise RuntimeError("Cannot find turingarena.conf config file")


def load_config():
    path = find_config_path()
    with open(path) as f:
        return toml.load(f)


class Config:
    def __init__(self):
        self.__dict__ = load_config()

    def __getitem__(self, item):
        return self.__dict__[item]

    def get(self, key, default=None):
        return self.__dict__.get(key, default)


config = Config()
