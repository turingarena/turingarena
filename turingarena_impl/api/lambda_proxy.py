import base64
import cgi
import json
import sys
from http import HTTPStatus

from io import BytesIO


def make_response(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body)
    }


def main(event, context):
    try:
        path = event["path"]
        query_parameters = event["queryStringParameters"] or {}
        request_headers = {
            key.lower(): value
            for key, value in (event["headers"] or {}).items()
        }

        lambda_body = event["body"]
        if lambda_body and not event["isBase64Encoded"]:
            return make_response(HTTPStatus.INTERNAL_SERVER_ERROR, dict(message="body must be base64 encoded"))

        request_body = lambda_body and base64.standard_b64decode(lambda_body)
        request_method = event["httpMethod"]

        if request_method not in ("GET", "POST"):
            return make_response(
                HTTPStatus.METHOD_NOT_ALLOWED,
                dict(message=f"Http method not allowed: {request_method}"),
            )

        if request_method == "POST":
            fields = cgi.FieldStorage(
                fp=BytesIO(request_body),
                environ=dict(
                    REQUEST_METHOD=request_method,
                    CONTENT_TYPE=request_headers["content-type"],
                    CONTENT_LENGTH=str(len(request_body)),
                ),
            )
        else:
            fields = None

        return make_response(HTTPStatus.OK, dict(pong=fields and fields.getfirst("ping")))
    except:
        return make_response(HTTPStatus.INTERNAL_SERVER_ERROR, dict(message=str(sys.exc_info())))
