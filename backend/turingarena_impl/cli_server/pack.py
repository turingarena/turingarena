import logging
import os
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from turingarena_common.commands import WorkingDirectory, GitCloneRepository, LocalExecutionParameters
from turingarena_impl.cli_server.git_manager import GitManager


@contextmanager
def enter_working_directory(working_directory: WorkingDirectory, *, local_execution):
    with create_working_directory(working_directory, local_execution=local_execution) as work_dir:
        old_cwd = os.curdir

        os.chdir(work_dir)
        os.chdir(working_directory.current_directory)

        yield

        os.chdir(old_cwd)


@contextmanager
def create_working_directory(working_directory: WorkingDirectory, *, local_execution=LocalExecutionParameters.DEFAULT):
    git = GitManager(local_execution.git_dir)
    git.init()

    with TemporaryDirectory() as temp_dir:
        logging.info(f"Unpacking working directory in {temp_dir}")

        for r in working_directory.pack.repositories:
            if isinstance(r, GitCloneRepository):
                git.fetch_repository(r)
            else:
                raise TypeError(type(r))

        git.checkout_trees(working_directory.pack.parts, temp_dir)
        yield temp_dir
