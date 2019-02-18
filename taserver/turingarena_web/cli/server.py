from abc import ABC
from argparse import ArgumentParser

from turingarena_web.cli.base import BASE_PARSER
from turingarena_web.cli.command import Command, add_subparser
from turingarena_web.model.database import database
from turingarena_web import create_app

class ServerCommand(Command, ABC):
    NAME = "server"
    PARSER = ArgumentParser(
        description="command to manage the server",
        parents=[BASE_PARSER],
        add_help=False,
    )


class InitDBCommand(ServerCommand):
    NAME = "initdb"
    PARSER = ArgumentParser(
        description="initialize the database",
        parents=[ServerCommand.PARSER],
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


class RunCommand(ServerCommand):
    NAME = "run"
    PARSER = ArgumentParser(
        description="run development server",
        parents=[ServerCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("--host", "-H", help="host where to listen", default="127.0.0.1")
    PARSER.add_argument("--port", "-p", help="port where to listen", default="8080")
    PARSER.add_argument("--debug", "-d", help="run in debug mode", action="store_true")

    def run(self):
        app = create_app()
        app.run(self.args.host, self.args.port, self.args.debug)


subparsers = ServerCommand.PARSER.add_subparsers(title="subcommand")
add_subparser(subparsers, RunCommand)
add_subparser(subparsers, InitDBCommand)
