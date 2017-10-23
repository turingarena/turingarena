"""TuringArena protocol proxy generator.

Usage:
  proxy [options]
"""

import docopt

from turingarena.protocol.proxy import generate_proxy


def protocol_proxy_cli(*, argv, protocol, dest_dir):
    args = docopt.docopt(__doc__, argv=argv)
    generate_proxy(protocol=protocol, dest_dir=dest_dir)
