import logging
import os
import sys
from functools import wraps

import coloredlogs
from docopt import docopt


def docopt_cli(fun):
    @wraps(fun)
    def wrapped(argv=None, **kwargs):
        if argv is None:
            argv = sys.argv[1:]
        args = docopt(doc=fun.__doc__, argv=argv, options_first=True)
        fun(args, **kwargs)

    return wrapped


def init_logger(args=None):
    if args is None:
        args = {
            "--log-level": None,
        }
    logger = logging.getLogger()
    level_name = args["--log-level"]
    if level_name is None:
        level_name = os.environ.get("TURINGARENA_LOG_LEVEL", None)
    if level_name is None:
        level_name = "warning"
    level = getattr(logging, level_name.upper())

    coloredlogs.install(
        logger=logger,
        level=level,
        fmt="%(asctime)s %(levelname)8s [%(process)5d] %(name)s: %(message)s",
        milliseconds=True,
    )
