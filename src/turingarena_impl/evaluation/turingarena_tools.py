from contextlib import contextmanager, ExitStack

from turingarena_impl.driver.server import SandboxServer


@contextmanager
def run_metaservers():
    with ExitStack() as stack:
        sandbox_dir = stack.enter_context(SandboxServer.run())
        yield dict(
            TURINGARENA_SANDBOX_DIR=sandbox_dir,
        )
