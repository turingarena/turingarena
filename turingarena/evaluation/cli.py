"""TuringArena evaluation.

Usage:
  evaluation [options] <task>

"""

import docopt

from turingarena.evaluation import EvaluationPlan, Task


def evaluation_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    plan = EvaluationPlan(Task(args["<task>"]))

    print(plan)
