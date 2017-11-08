"""TuringArena evaluation.

Usage:
  compute [options] [--entry <id>...] [--dep <id>...]

Options:
  --task=<task>  Task name (i.e., the command that generates its description)
  --dep=<id>  Specify the id of a dependency
  --entry=<id>  Specify the id of an entry

"""

import docopt

from turingarena.evaluation import compute_task


def evaluation_compute_cli(argv, **kwargs):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    return compute_task(
        task=args["--task"],
        deps=args["--dep"],
        entries=args["--entry"],
        **kwargs,
    )
