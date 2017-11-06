"""TuringArena evaluation.

Usage:
  evaluation [options] <task>

"""

import docopt

from turingarena.evaluation import EvaluationPlan, Task, evaluate_task


def evaluation_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)
    evaluate_task(Task(args["<task>"]))
