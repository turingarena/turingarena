"""TuringArena task describe CLI.

Usage:
  describe
"""

import docopt
import importlib

from turingarena.problem import ProblemIdentifier
from turingarena.problem.entry_cli import problem_entry_cli
from turingarena.problem.goal_cli import problem_goal_cli


def task_describe_cli(*, task, argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)
    print(task.all_phases())
