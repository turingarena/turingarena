import base64
import cgi
import json
from http import HTTPStatus
from io import BytesIO

from turingarena_impl.api.common import ProxyError, execute_api
from turingarena_impl.api.dummy_impl import endpoints


def main(event, context):
    http_method = event["httpMethod"]
    path = event["path"]

    status_code, body = execute_api(
        endpoints,
        http_method,
        path,
        get_query=lambda: get_query(event),
        get_fields=lambda: get_fields(event),
    )

    return {
        "statusCode": status_code,
        "body": json.dumps(body, indent=4)
    }


def get_query(event):
    return event["queryStringParameters"] or {}


def get_fields(event):
    request_headers = {
        key.lower(): value
        for key, value in (event["headers"] or {}).items()
    }

    lambda_body = event["body"]
    if lambda_body and not event["isBase64Encoded"]:
        raise ProxyError(HTTPStatus.INTERNAL_SERVER_ERROR, dict(message="body must be base64 encoded"))
    request_body = lambda_body and base64.standard_b64decode(lambda_body)

    return cgi.FieldStorage(
        fp=BytesIO(request_body),
        environ=dict(
            REQUEST_METHOD="POST",
            CONTENT_TYPE=request_headers["content-type"],
            CONTENT_LENGTH=str(len(request_body)),
        ),
    )
