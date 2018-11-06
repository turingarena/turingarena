from argparse import ArgumentParser

from .base import BASE_PARSER
from .command import Command


class LoginCommand(Command):
    PARSER = ArgumentParser(
        description="Login into TuringArena Cloud system",
        parents=[BASE_PARSER],
        add_help=False,
    )

    def run(self):
        raise NotImplementedError

