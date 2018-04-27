import sys
from functools import wraps

from docopt import docopt


def docopt_cli(fun):
    @wraps(fun)
    def wrapped(argv=None, **kwargs):
        if argv is None:
            argv = sys.argv[1:]
        args = docopt(doc=fun.__doc__, argv=argv, options_first=True)
        fun(args, **kwargs)

    return wrapped
