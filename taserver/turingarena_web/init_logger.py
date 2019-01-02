import coloredlogs
import logging
import os


from turingarena_web.config import config


logger = logging.getLogger()


def init_logger(level_name=None, isatty=False):
    if level_name is None:
        level_name = os.environ.get("TURINGARENA_LOG_LEVEL")
    if level_name is None:
        level_name = config.get("log_level")
    if level_name is None:
        level_name = "warning"
    level = getattr(logging, level_name.upper())

    coloredlogs.install(
        logger=logger,
        level=level,
        fmt="%(asctime)s %(levelname)8s [%(process)5d] %(name)s: %(message)s",
        milliseconds=True,
        isatty=isatty,
    )
