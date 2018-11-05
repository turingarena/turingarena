import logging
import argparse

from wsgiref.simple_server import make_server

from turingarena.api.wsgi_proxy import application


def serve_cli():
    parser = argparse.ArgumentParser("Serve cli")
    parser.add_argument("--host", "-H", help="Address where to listen", default="0.0.0.0")
    parser.add_argument("--port", "-p", help="Port where to listen", default="8000", type=int)
    args = parser.parse_args()

    host = args.host
    port = args.port

    logging.root.setLevel(logging.DEBUG)
    print(f"Serving on {host}:{port}...")
    with make_server(host, port, app=application) as httpd:
        httpd.serve_forever()


if __name__ == '__main__':
    serve_cli()
