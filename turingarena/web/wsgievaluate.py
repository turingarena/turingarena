import cgi
import json
import traceback

from turingarena.web.formevaluate import form_evaluate


def application(environ, start_response):
    headers = [("Access-Control-Allow-Origin", "*")]
    try:
        fields = cgi.FieldStorage(environ=environ, fp=environ["wsgi.input"])
        response = form_evaluate(fields)
    except:
        start_response("500 Internal Server Error", headers)
        yield json.dumps({
            "error": {
                "message": traceback.format_exc(),
            },
        }).encode()
    else:
        start_response("200 OK", headers)
        yield response.encode()
