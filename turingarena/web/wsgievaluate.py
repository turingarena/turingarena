import cgi
import traceback

from turingarena.web.formevaluate import form_evaluate


def application(environ, start_response):
    try:
        fields = cgi.FieldStorage(environ=environ)
        response = form_evaluate(fields)
    except:
        start_response("500 Internal Server Error", [])
        yield traceback.format_exc().encode()
    else:
        start_response("200 OK", [])
        yield response["stdout"].encode()
