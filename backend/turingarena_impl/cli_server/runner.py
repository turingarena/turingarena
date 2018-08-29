import pickle
import sys

from turingarena_common.commands import EvaluateCommandParameters


def run_evaluate_command(command: EvaluateCommandParameters):
    print("EVALUATE COMMAND", file=sys.stderr)


COMMANDS_MAP = {
    EvaluateCommandParameters: run_evaluate_command,
}


def do_main(args):
    for t, runner in COMMANDS_MAP.items():
        if isinstance(args, t):
            return runner(args)
    print(args, file=sys.stderr)
    raise TypeError(type(args))


def main():
    parameters = pickle.load(sys.stdin.buffer)
    do_main(parameters)


if __name__ == '__main__':
    main()
