from turingarena.cli import docopt_cli
from turingarena.sandbox.server import sandbox_run


@docopt_cli
def main(args):
    """TuringArena sandbox.

    Runs the given algorithm in a sandbox.

    Usage:
      turingarena-sandbox <algorithm-dir>

    Options:
      <algorithm-dir>  Directory containing the algorithm to run

    """

    sandbox_run(algorithm_dir=args["<algorithm-dir>"])
