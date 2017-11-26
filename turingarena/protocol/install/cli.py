"""TuringArena protocol installer.

Usage:
  install [options]

Options:
"""

import docopt

from turingarena.protocol.install import install_protocol


def protocol_install_cli(*, argv, protocol_name):
    args = docopt.docopt(__doc__, argv=argv)
    install_protocol(protocol_name=protocol_name)
