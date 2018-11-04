import os
import sys

from turingarena_common.commands import FileCommandParameters, LocalExecutionParameters, FileCatCommandParameters

from turingarena_impl.cli_server.pack import create_working_directory
from turingarena_impl.file.generated import PackGeneratedDirectory


def file_cmd(parameters: FileCommandParameters, local_execution: LocalExecutionParameters):
    command = parameters.command
    for t, runner in COMMANDS_MAP.items():
        if isinstance(command, t):
            return runner(command, parameters.working_directory, local_execution=local_execution)
    raise TypeError(type(command))


def file_cat_cmd(parameters: FileCatCommandParameters, working_directory, local_execution):
    with create_working_directory(working_directory, local_execution=local_execution) as work_dir:
        generated = PackGeneratedDirectory(work_dir)
        path = os.path.join(working_directory.current_directory, parameters.path)
        generated.cat_file(path, file=sys.stdout)


COMMANDS_MAP = {
    FileCatCommandParameters: file_cat_cmd,
}
