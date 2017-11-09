"""TuringArena maker manager.

Usage:
  make [options] [--entry <entry>]... [--] <target>

Options:
  --compute-command=<command>  The command to run to execute a task.
      [default: turingarena compute --db ~/.turingarena/db.git]
  --entry <entry>  Add an entry, with format <name>:<id>
  <target>  The task to make

"""
import docopt
from functools import partial

from turingarena.make import SequentialMaker, subprocess_compute


def make_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    maker = SequentialMaker(
        target=args["<target>"],
        compute=partial(
            subprocess_compute,
            compute_command=args["--compute-command"],
        ),
        entries=dict(
            entry_option.split(":")
            for entry_option in args["--entry"]
        )
    )

    print(maker.run())
