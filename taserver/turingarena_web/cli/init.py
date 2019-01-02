from abc import ABC
from argparse import ArgumentParser

from turingarena_web.cli.base import BASE_PARSER
from turingarena_web.cli.command import Command
from turingarena_web.model.database import database


class InitCommand(Command, ABC):
    NAME = "init"
    PARSER = ArgumentParser(
        description="initialize the database",
        parents=[BASE_PARSER],
        add_help=False,
    )

    def run(self):
        database.init()
