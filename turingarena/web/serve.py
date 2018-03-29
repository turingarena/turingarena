from wsgiref.simple_server import make_server

from turingarena.cli import docopt_cli
from turingarena.web.wsgievaluate import application


@docopt_cli
def serve_cli(args):
    """
    Usage:
        serve [options]

    Options:
        --host=<host>  Address where to listen. [default: 0.0.0.0]
        -p --port=<port>  Port where to listen. [default: 8000]

    """
    host = args["--host"]
    port = int(args["--port"])
    print(f"Serving on {host}:{port}...")
    with make_server(host, port, app=application) as httpd:
        httpd.serve_forever()
