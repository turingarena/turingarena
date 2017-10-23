"""TuringArena container client.

Usage:
  container [options] exec [-i <input>]... [-o <output>]... [--] <cmd>...
  container [options] import <dir>
  container [options] export <id>

Options:

  -i --input=<input>  Declares an input directory. Format: <dir>:<data-id>
  -o --output=<output>  Declares an output directory.
  -n --name  Container name
  <cmd>  Command to run

"""

import requests
import requests_unixsocket

from docopt import docopt

requests_unixsocket.monkeypatch()


def container_client_cli(argv):
    print(argv)
    args = docopt(__doc__, argv=argv, options_first=True)

    if args["exec"]:
        requests.get('http+unix://%2Frun%2Fturingarena-container%2F.sock/path/to/page')
