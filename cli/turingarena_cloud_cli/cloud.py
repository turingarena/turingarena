from abc import ABC
from argparse import ArgumentParser
from functools import lru_cache
from time import sleep

import requests

from .base import BASE_PARSER
from .command import Command


TURINGARENA_DEFAULT_ENDPOINT = "https://api.turingarena.org"


class CloudServerError(Exception):
    pass


def exponential_backoff(function, initial_wait=5, initial_backoff=0.4, backoff_factor=2):
    sleep(initial_wait)
    backoff = initial_backoff
    while True:
        res = function()
        if res is not None:
            return res

        sleep(backoff)
        backoff *= backoff_factor


class CloudCommand(Command, ABC):
    PARSER = ArgumentParser(
        description="Use TuringArena cloud infrastructure",
        parents=[BASE_PARSER],
        add_help=False,
    )
    PARSER.add_argument("repository", help="repository")
    PARSER.add_argument("--endpoint", help="cloud API endpoint")
    PARSER.add_argument("--oid", "-i", help="commit/tree OID", default="FETCH_HEAD")
    PARSER.add_argument("--directory", "-d", help="specify a subdirectory inside the repository", default=".")

    @property
    def endpoint(self):
        if self.args.endpoint is not None:
            return self.args.endpoint
        return TURINGARENA_DEFAULT_ENDPOINT

    @property
    def parameters(self):
        return {
            "oid": self.args.oid,
            "repository[url]": self.args.repository,
            "directory": self.args.directory,
        }

    @property
    @lru_cache(None)
    def repository_exists(self):
        response = requests.get("https://api.github.com/repos/{}".format(self.args.repository))
        return response.status_code == 200
