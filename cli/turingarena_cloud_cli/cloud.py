from abc import ABC
from argparse import ArgumentParser

from .base import BASE_PARSER
from .command import Command


TURINGARENA_DEFAULT_ENDPOINT = "https://api.turingarena.org"


class CloudServerError(Exception):
    pass


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
