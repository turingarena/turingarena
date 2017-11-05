"""TuringArena protocol proxy generator.

Usage:
  proxy [options]

Options:
  -x --language=<lang>  Language to use [default: python]
  -o --output-dir=<output-dir>  Directory where to generate code [default: ./generated]
"""

import docopt

from turingarena.protocol.proxy import generate_proxy


def protocol_proxy_cli(*, argv, protocol_id):
    args = docopt.docopt(__doc__, argv=argv)
    generate_proxy(
        protocol_id=protocol_id,
        language=args["--language"],
    )
