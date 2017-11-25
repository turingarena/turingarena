"""TuringArena task run CLI.

Usage:
  run --phase=<name> [--index=<index>]

Options:
  --phase=<name>  Name of the phase to run
  --index=<index>  Index of the specific parametrization of the phase to run
"""

import docopt
import importlib

from turingarena.problem import ProblemIdentifier
from turingarena.problem.entry_cli import problem_entry_cli
from turingarena.problem.goal_cli import problem_goal_cli


def task_run_cli(*, task, argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)
    task.run_phase(phase_name=args["--phase"])
