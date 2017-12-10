from turingarena.cli import docopt_cli
from turingarena.sandbox.run import sandbox_run


@docopt_cli
def sandbox_cli(args):
    """TuringArena sandbox manager.

    Usage:
      sandbox [options] <cmd> [<args>]...

    Options:
      -h --help  Show this help.
    """

    commands = {
        "run": sandbox_run_cli,
    }

    argv2 = args["<args>"]
    command = args["<cmd>"]

    commands[command](argv2)


@docopt_cli
def sandbox_run_cli(args):
    """TuringArena sandbox run.

    Runs the given algorithm in a sandbox.

    Usage:
      run [options] <algorithm-dir>

    Options:
      <algorithm-dir>  Directory containing the algorithm to run

    """

    sandbox_run(algorithm_dir=args["<algorithm-dir>"])
