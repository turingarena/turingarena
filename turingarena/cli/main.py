from turingarena.cli import docopt_cli

from turingarena.cli.loggerinit import init_logger
from turingarena.container.cli import container_cli
from turingarena.problem import problem_evaluate_cli
from turingarena.protocol.template import generate_template_cli, generate_skeleton_cli


@docopt_cli
def main(args):
    """TuringArena command line interface.

    Usage:
      turingarena [options] <cmd> [<args>]...

    Options:
      --log-level=<level>  Set logging level.
    """
    init_logger(args)

    commands = {
        "container": container_cli,
        "evaluate": problem_evaluate_cli,
        "template": generate_template_cli,
        "skeleton": generate_skeleton_cli,
    }
    argv2 = args["<args>"]
    commands[args["<cmd>"]](argv2)


if __name__ == '__main__':
    main()
