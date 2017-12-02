from turingarena.cli import docopt_cli
from turingarena.sandbox.compile import sandbox_compile
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
        "compile": sandbox_compile_cli,
        "run": sandbox_run_cli,
    }

    argv2 = args["<args>"]
    command = args["<cmd>"]

    commands[command](argv2)


@docopt_cli
def sandbox_compile_cli(args):
    """TuringArena algorithm compiler.

    Usage:
      compile [options] <source>

    Options:

      <source>  Source file of the algorithm
      -I --interface=<interface>  Name of the interface this algorithm implements
      -p --protocol=<interface>  Name of the protocol there the interface is defined
      -x --language=<lang>  Language in which the algorithm is written
      -o --algorithm=<name>  Name of the algorithm to generate

    """

    sandbox_compile(
        source_filename=args["<source>"],
        language=args["--language"],
        protocol_name=args["--protocol"],
        interface_name=args["--interface"],
        algorithm_name=args["--algorithm"],
    )


@docopt_cli
def sandbox_run_cli(args):
    """TuringArena sandbox run.

    Runs the given algorithm in a sandbox.

    Usage:
      run [options] <algorithm>

    Options:
      <algorithm>  Algorithm to run

    """

    sandbox_run(args["<algorithm>"])
