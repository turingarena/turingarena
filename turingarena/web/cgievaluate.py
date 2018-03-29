"""
Evaluate a solution provided via a Web form (CGI).
"""
import cgi
import sys
import traceback

from turingarena.web.formevaluate import form_evaluate


def evaluate():
    fields = cgi.FieldStorage()

    try:
        evaluation = form_evaluate(fields)
    except:
        print("500 Internal Server Error")
        print("Access-Control-Allow-Origin:", "*")
        print()
        traceback.print_exc(file=sys.stdout)
        raise

    print("200 OK")
    print("Access-Control-Allow-Origin:", "*")
    print()
    print(evaluation)


if __name__ == "__main__":
    evaluate()
