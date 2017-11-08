"""TuringArena evaluation.

Usage:
  entry [options] [--file <file>...]

Options:
  --name=<name>  Name of the entry to create
  --file=<file>  Files to add to this entry

"""

import docopt

from turingarena.evaluation import evaluate_task, make_entry


def evaluation_entry_cli(argv, **kwargs):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    return make_entry(
        name=args["--name"],
        file_map={f: f for f in args["--file"]},
        **kwargs,
    )
