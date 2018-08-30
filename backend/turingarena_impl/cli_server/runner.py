import logging
import pickle
import sys

from turingarena_common.commands import EvaluateCommandParameters, DaemonCommandParameters
from turingarena_impl.cli_server.evaluate import evaluate_cmd
from turingarena_impl.logging import init_logger

COMMANDS_MAP = {
    EvaluateCommandParameters: evaluate_cmd,
}


def run_command(command_parameters):
    for t, runner in COMMANDS_MAP.items():
        if isinstance(command_parameters, t):
            return runner(command_parameters)
    raise TypeError(type(command_parameters))


def do_main(parameters: DaemonCommandParameters):
    init_logger(parameters.log_level, parameters.stderr_isatty)
    logging.debug(f"Running command {parameters}")
    return run_command(parameters.command)


def main():
    parameters = pickle.load(sys.stdin.buffer)
    do_main(parameters)


if __name__ == '__main__':
    main()
