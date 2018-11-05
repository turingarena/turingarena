import logging
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena_common.commands import WorkingDirectory, LocalExecutionParameters
from turingarena_impl.cli_server.git_manager import GitManager


@contextmanager
def create_working_directory(working_directory: WorkingDirectory, *, local_execution=LocalExecutionParameters.DEFAULT):
    git = GitManager(local_execution.git_dir)
    git.init()

    with TemporaryDirectory() as temp_dir:
        logging.info(f"Unpacking working directory in {temp_dir}")

        if working_directory.pack.repository is not None:
            git.fetch_repository(working_directory.pack.repository)
        git.checkout_commit(working_directory.pack.oid, temp_dir)

        yield temp_dir
