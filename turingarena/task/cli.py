"""TuringArena task CLI.

Usage:
  task [options] -m <module> [-n <name>] <cmd> [<args>...]

Options:

  -m --module=<package>  Python module containing the problem definition
  -n --name=<name>  Qualified name of the problem variable [default: problem]

"""

import docopt
import importlib

from turingarena.task.describe_cli import task_describe_cli
from turingarena.task.run_cli import task_run_cli


def task_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    module = importlib.import_module(args["--module"])
    task = getattr(module, args["--name"])

    commands = {
        "describe": task_describe_cli,
        "run": task_run_cli,
    }
    argv2 = args["<args>"]
    return commands[args["<cmd>"]](task=task, argv=argv2)
