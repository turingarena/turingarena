"""TuringArena protocol skeleton generator.

Usage:
  skeleton [options]
"""

import docopt

from turingarena.protocol.skeleton import generate_skeleton


def protocol_skeleton_cli(*, argv, protocol, dest_dir):
    args = docopt.docopt(__doc__, argv=argv)
    generate_skeleton(protocol=protocol, dest_dir=dest_dir)
