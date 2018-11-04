import logging
import pickle
import sys

from turingarena_common.commands import EvaluateCommandParameters, RemoteCommandParameters, LocalExecutionParameters, \
    FileCommandParameters, InfoCommandParameters, TestCommandParameters
from turingarena_impl.cli_server.evaluate import evaluate_cmd
from turingarena_impl.cli_server.files import file_cmd
from turingarena_impl.cli_server.info import info_cmd
from turingarena_impl.cli_server.test import test_cmd
from turingarena_impl.logging import init_logger

COMMANDS_MAP = {
    EvaluateCommandParameters: evaluate_cmd,
    FileCommandParameters: file_cmd,
    InfoCommandParameters: info_cmd,
    TestCommandParameters: test_cmd,
}


def run_command(command_parameters, local_execution):
    for t, runner in COMMANDS_MAP.items():
        if isinstance(command_parameters, t):
            return runner(command_parameters, local_execution)
    raise TypeError(type(command_parameters))


def do_main(parameters: RemoteCommandParameters):
    init_logger(parameters.log_level, parameters.stderr_isatty)
    local_execution = parameters.local_execution
    if local_execution is None:
        local_execution = LocalExecutionParameters.DEFAULT

    logging.debug(f"Running command {parameters}")
    return run_command(parameters.command, local_execution)


def main():
    parameters = pickle.load(sys.stdin.buffer)
    do_main(parameters)


if __name__ == '__main__':
    main()
