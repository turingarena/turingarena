"""
Evaluate a solution provided via a Web form (using Hyper.sh conventions).
"""

import sys

sys.stderr = sys.stdout

import cgi
import os
import traceback

from turingarena.web.formevaluate import form_evaluate


def evaluate():
    fields = cgi.FieldStorage(
        environ=dict(REQUEST_METHOD="POST"),
        headers={
            "content-type": os.environ["content_type"],
        }
    )

    try:
        evaluation = form_evaluate(fields)
    except:
        print("ERROR during evaluation:")
        traceback.print_exc()
        raise

    print(evaluation)


if __name__ == "__main__":
    evaluate()
