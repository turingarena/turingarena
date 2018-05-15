import cgi
import json
from http import HTTPStatus
from urllib.parse import parse_qsl

from turingarena_impl.api.common import execute_api
from turingarena_impl.api.dummy_impl import endpoints


def get_fields(environ):
    return cgi.FieldStorage(environ=environ, fp=environ["wsgi.input"])


def get_query(environ):
    return {
        k: v
        for k, v in parse_qsl(environ['QUERY_STRING'])
    }


def application(environ, start_response):
    request_method = environ["REQUEST_METHOD"]
    path = environ["PATH_INFO"]

    status_code, body = execute_api(
        endpoints,
        request_method,
        path,
        get_query=lambda: get_query(environ),
        get_fields=lambda: get_fields(environ),
    )

    status_description = HTTPStatus(status_code).description
    headers = [("Access-Control-Allow-Origin", "*")]
    start_response(f"{status_code} {status_description}", headers)
    yield (json.dumps(body, indent=4) + "\n").encode()
