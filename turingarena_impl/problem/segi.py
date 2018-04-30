"""
Submission Evaluation Gateway Interface
"""
import os
from contextlib import contextmanager, ExitStack

from turingarena_impl.interface.driver import DriverServer
from turingarena_impl.sandbox.server import SandboxServer


@contextmanager
def run_metaservers():
    with ExitStack() as stack:
        sandbox_dir = stack.enter_context(SandboxServer.run())
        driver_dir = stack.enter_context(DriverServer.run())
        stack.enter_context(env_extension(
            TURINGARENA_SANDBOX_DIR=sandbox_dir,
            TURINGARENA_DRIVER_DIR=driver_dir,
        ))
        yield


@contextmanager
def env_extension(**d):
    old_env = os.environ
    os.environ = {**old_env, **d}
    try:
        yield
    finally:
        os.environ = old_env
