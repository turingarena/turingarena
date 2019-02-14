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
        print("Really initialize the database?")
        print("WARNING: all existing database data will be lost!!!")
        print("Type the string \"yes, I know what I'm doing\" to do so: ", end="")
        if input() == "yes, I know what I'm doing":
            database.init()
        else:
            print("Aborted")
