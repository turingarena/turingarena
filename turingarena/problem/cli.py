"""TuringArena problem CLI.

Usage:
  problem [options] -m <module> [-n <name>] <cmd> [<args>...]

Options:

  -m --module=<package>  Python module containing the problem definition
  -n --name=<name>  Qualified name of the problem variable [default: problem]

"""

import docopt

from turingarena.problem import ProblemIdentifier
from turingarena.problem.entry_cli import problem_entry_cli
from turingarena.problem.goal_cli import problem_goal_cli


def problem_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    problem_id = ProblemIdentifier(
        module=args["--module"],
        name=args["--name"],
    )

    commands = {
        "goal": problem_goal_cli,
        "entry": problem_entry_cli,
    }
    argv2 = args["<args>"]
    return commands[args["<cmd>"]](problem_id=problem_id, argv=argv2)
