import logging
import os

import coloredlogs


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
        level_name = "info"
    level = getattr(logging, level_name.upper())

    coloredlogs.install(
        logger=logger,
        level=level,
        fmt="%(asctime)s %(levelname)8s [%(process)5d] %(name)s: %(message)s",
        milliseconds=True,
    )
