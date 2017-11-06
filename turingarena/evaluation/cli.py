"""TuringArena evaluation.

Usage:
  evaluation [options] task <task>
  evaluation [options] entry <name> <files>...

"""

import docopt

from turingarena.evaluation import Task, evaluate_task, make_entry


def evaluation_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    if args["task"]:
        return evaluate_task(Task(args["<task>"]))

    if args["entry"]:
        return make_entry(
            name=args["<name>"],
            file_map={f: f for f in args["<files>"]},
        )
