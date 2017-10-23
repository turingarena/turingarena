import logging
import os

import coloredlogs


def init_logger(args):
    logger = logging.getLogger()
    levels = [
        logging.WARNING,
        logging.INFO,
        logging.DEBUG,
    ]
    level_name = args["--log-level"]
    if level_name is None:
        level_name = os.environ.get("TURINGARENA_LOG_LEVEL", None)
    if level_name is None:
        level_name = "info"
    level = getattr(logging, level_name.upper())
    coloredlogs.install(
        logger=logger,
        level=level,
        fmt="%(levelname)8s [%(process)5d] %(name)s: %(message)s",
    )
