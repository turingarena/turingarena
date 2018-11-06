import sys
from abc import ABC
from argparse import ArgumentParser
from time import sleep

import requests

from .base import BASE_PARSER
from .command import Command


TURINGARENA_DEFAULT_ENDPOINT = "https://api.turingarena.org"


class CloudServerError(Exception):
    pass


def exponential_backoff(initial_wait=0, initial_backoff=0.4, backoff_factor=2):
    sleep(initial_wait)
    backoff = initial_backoff
    while True:
        yield
        sleep(backoff)
        backoff *= backoff_factor


class CloudCommand(Command, ABC):
    PARSER = ArgumentParser(
        description="Use TuringArena cloud infrastructure",
        parents=[BASE_PARSER],
        add_help=False,
    )
    PARSER.add_argument("--endpoint", help="cloud API endpoint")

    @property
    def endpoint(self):
        if self.args.endpoint is not None:
            return self.args.endpoint
        return TURINGARENA_DEFAULT_ENDPOINT

    def check_repository_exists(self):
        response = requests.get("https://api.github.com/repos/{}".format(self.args.repository))
        if response.status_code != 200:
            print("ERROR: the repository {} doesn't exists on GitHub".format(self.args.repository), file=sys.stderr)
            exit(1)
