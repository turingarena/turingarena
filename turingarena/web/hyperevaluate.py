"""
Evaluate a solution provided via a Web form (using Hyper.sh conventions).
"""

import cgi
import os
import sys
import traceback

from turingarena.web.formevaluate import form_evaluate


def main():
    sys.stderr = sys.stdout

    debug = "debug" in os.environ

    if debug:
        print(os.environ)

    fields = cgi.FieldStorage(
        environ=dict(
            REQUEST_METHOD="POST",
            CONTENT_TYPE=os.environ["content_type"],
            CONTENT_LENGTH=os.environ["content_length"],
        ),
    )
    if debug:
        print(fields)

    try:
        evaluation = form_evaluate(fields)
    except:
        print("ERROR during evaluation:")
        traceback.print_exc()
        raise

    print(evaluation)


if __name__ == "__main__":
    main()
