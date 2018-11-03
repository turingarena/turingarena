import os
from contextlib import ExitStack

import sys

from turingarena_common.commands import FileCommandParameters, LocalExecutionParameters, FileCatCommandParameters
from turingarena_impl.cli_server.pack import create_working_directory
from turingarena_impl.file.generated import PackGeneratedDirectory


def file_cmd(parameters: FileCommandParameters, local_execution: LocalExecutionParameters):
    with ExitStack() as stack:
        work_dir = stack.enter_context(create_working_directory(
            parameters.working_directory,
            local_execution=local_execution,
        ))

        command = parameters.command
        for t, runner in COMMANDS_MAP.items():
            if isinstance(command, t):
                return runner(command, work_dir, parameters.working_directory.current_directory)
        raise TypeError(type(command))


def file_cat_cmd(parameters: FileCatCommandParameters, working_directory, current_directory):
    with create_working_directory(working_directory) as work_dir:
        generated = PackGeneratedDirectory(work_dir)
        path = os.path.join(current_directory, parameters.path)
        generated.cat_file(path, file=sys.stdout)


COMMANDS_MAP = {
    FileCatCommandParameters: file_cat_cmd,
}
