"""TuringArena task CLI.

Usage:
  task [options] -m <module> [-n <name>] <cmd> [<args>...]

Options:

  -m --module=<package>  Python module containing the problem definition
  -n --name=<name>  Qualified name of the problem variable [default: problem]

"""

import docopt
import importlib

from turingarena.make import resolve_plan
from turingarena.make.describe_cli import make_describe_cli
from turingarena.make.run_cli import make_run_cli


def make_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    plan_module = importlib.import_module(args["--module"])
    plan_descriptor = getattr(plan_module, args["--name"])
    plan = resolve_plan(plan_descriptor.get_tasks())

    commands = {
        "describe": make_describe_cli,
        "run": make_run_cli,
    }
    argv2 = args["<args>"]
    return commands[args["<cmd>"]](plan=plan, argv=argv2)
