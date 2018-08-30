import argparse

LOG_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", ]

BASE_PARSER = argparse.ArgumentParser(
    description="Turingarena CLI",
    add_help=False,
)
BASE_PARSER.add_argument(
    "--log-level",
    help="log level ({})".format(",".join(LOG_LEVELS)),
    type=str.upper,
    metavar="LEVEL",
    choices=LOG_LEVELS,
    default="WARNING",
)
