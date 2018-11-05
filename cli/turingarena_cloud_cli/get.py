from argparse import ArgumentParser

from .command import Command
from .base import BASE_PARSER


class GetCommand(Command):
    PARSER = ArgumentParser(
        description="Get a problem from TuringArena",
        parents=[BASE_PARSER],
        add_help=False,
    )

    def run(self):
        raise NotImplementedError
