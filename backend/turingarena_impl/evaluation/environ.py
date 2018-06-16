import os
from contextlib import contextmanager


@contextmanager
def env_extension(d):
    old_env = dict(os.environ)
    os.environ.update(d)
    try:
        yield
    finally:
        os.environ.update(old_env)
        for k in d:
            if k not in old_env:
                del os.environ[k]
