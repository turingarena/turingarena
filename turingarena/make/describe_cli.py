"""TuringArena task describe CLI.

Usage:
  describe
"""
import json

import docopt

from turingarena.make import make_plan_signature


def make_describe_cli(*, plan, argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)
    print(json.dumps(make_plan_signature(plan), indent=2))
