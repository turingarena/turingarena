import traceback
from http import HTTPStatus


class ProxyError(Exception):
    def __init__(self, status_code, body):
        pass


def get_method(endpoints, http_method, path):
    if not path:
        path = "/"
    assert path.startswith("/")

    try:
        endpoint = endpoints[path[1:]]
    except KeyError:
        raise ProxyError(HTTPStatus.NOT_FOUND, dict(message=f"Unknown endpoint {path}"))

    try:
        return endpoint[http_method]
    except KeyError:
        raise ProxyError(HTTPStatus.METHOD_NOT_ALLOWED, dict(message=f"Method not allowed: {http_method}"))


def execute_api(endpoints, http_method, path, *, get_query, get_fields):
    try:
        method = get_method(endpoints, http_method, path)

        if http_method == "GET":
            params = get_query()
        else:
            params = get_fields()

        return HTTPStatus.OK, method(params)
    except ProxyError as e:
        return e.args
    except:
        traceback.print_exc()
        return HTTPStatus.INTERNAL_SERVER_ERROR, dict(message=traceback.format_exc())
