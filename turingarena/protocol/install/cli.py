"""TuringArena protocol installer.

Usage:
  install [options]

Options:
"""

import docopt

from turingarena.protocol.install import install_protocol
from turingarena.protocol.proxy import generate_proxy


def protocol_install_cli(*, argv, protocol_id):
    args = docopt.docopt(__doc__, argv=argv)
    install_protocol(protocol_id=protocol_id)
