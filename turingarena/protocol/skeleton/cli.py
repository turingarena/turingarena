"""TuringArena protocol skeleton generator.

Usage:
  skeleton [options]

Options:
  -o --output-dir=<dir>  Output directory [default: ./generated_skeletons]
"""

import docopt

from turingarena.protocol.skeleton import generate_skeleton


def protocol_skeleton_cli(*, argv, protocol):
    args = docopt.docopt(__doc__, argv=argv)
    generate_skeleton(protocol=protocol, dest_dir=args["--output-dir"])
