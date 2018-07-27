import logging
import os

import coloredlogs
from termcolor import colored

logger = logging.getLogger()


def init_logger(level_name=None):
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


def error(string):
    print(colored("==> ERROR:", "red", attrs=["bold"]), string)


def warning(string):
    print(colored("==> WARNING:", "yellow", attrs=["bold"]), string)


def ok(string):
    print(colored("==>", "green", attrs=["bold"]), string)


def info(string):
    print(colored("  ->", "blue", attrs=["bold"]), string)