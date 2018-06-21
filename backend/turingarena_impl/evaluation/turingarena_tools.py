from contextlib import contextmanager, ExitStack

from turingarena_impl.driver.interface.driver import DriverServer
from turingarena_impl.driver.server import SandboxServer


@contextmanager
def run_metaservers():
    with ExitStack() as stack:
        sandbox_dir = stack.enter_context(SandboxServer.run())
        driver_dir = stack.enter_context(DriverServer.run())
        yield dict(
            TURINGARENA_SANDBOX_DIR=sandbox_dir,
            TURINGARENA_DRIVER_DIR=driver_dir,
        )
