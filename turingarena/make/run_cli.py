"""TuringArena task run CLI.

Usage:
  run --phase=<name> [--index=<index>]

Options:
  --phase=<name>  Name of the phase to run
  --index=<index>  Index of the specific parametrization of the phase to run
"""

import docopt


def make_run_cli(*, plan, argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)
    phase_name = args["--phase"]
    plan[phase_name].run()
