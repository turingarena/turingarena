"""
Evaluate a solution provided via a Web form (using Hyper.sh conventions).
"""

import cgi
import json
import os
import sys
import traceback

from turingarena_impl.web.formevaluate import form_evaluate


def main():
    sys.stderr = sys.stdout

    try:
        response = do_evaluate()
    except:
        response = json.dumps({
            "error": {
                "message": traceback.format_exc(),
            },
        })

    print(response)


def do_evaluate():
    fields = cgi.FieldStorage(
        environ=dict(
            REQUEST_METHOD="POST",
            CONTENT_TYPE=os.environ["content_type"],
            CONTENT_LENGTH=os.environ["content_length"],
        ),
    )
    evaluation = form_evaluate(fields)
    return evaluation


if __name__ == "__main__":
    main()
