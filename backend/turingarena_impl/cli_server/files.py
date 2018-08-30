import logging
from contextlib import ExitStack

from turingarena_common.commands import FileCommandParameters, LocalExecutionParameters, FileCatCommandParameters
from turingarena_impl.cli_server.pack import enter_working_directory


def file_cmd(parameters: FileCommandParameters, local_execution: LocalExecutionParameters):
    with ExitStack() as stack:
        stack.enter_context(enter_working_directory(
            parameters.working_directory,
            local_execution=local_execution,
        ))

        command = parameters.command
        for t, runner in COMMANDS_MAP.items():
            if isinstance(command, t):
                return runner(command)
        raise TypeError(type(command))


def file_cat_cmd(parameters: FileCatCommandParameters):
    logging.warning("file cat")


COMMANDS_MAP = {
    FileCatCommandParameters: file_cat_cmd,
}
