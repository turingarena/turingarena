import os
from contextlib import ExitStack

import pytest
from turingarena_impl.cli_server.pack import create_working_directory


def test_cmd(parameters, local_execution):
    with ExitStack() as stack:
        work_dir = stack.enter_context(create_working_directory(
            parameters.working_directory,
            local_execution=local_execution,
        ))

        os.chdir(work_dir)
        cli = ["-p", "no:cacheprovider", "-n", "8"]
        if parameters.pytest_arguments:
            cli += parameters.pytest_arguments
        return_code = pytest.main(cli)
        exit(return_code)
