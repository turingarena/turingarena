from abc import ABC
from argparse import ArgumentParser

from tabulate import tabulate
from turingarena_web.problem import install_problem, update_problem, delete_problem
from turingarena_web.cli.base import BASE_PARSER
from turingarena_web.cli.command import Command, add_subparser
from turingarena_web.database import database


class ProblemCommand(Command, ABC):
    NAME = "problem"
    PARSER = ArgumentParser(
        description="Manipulate TuringArena problem",
        parents=[BASE_PARSER],
        add_help=False,
    )


class InstallProblemCommand(ProblemCommand):
    NAME = "install"
    PARSER = ArgumentParser(
        description="add a problem to TuringArena",
        parents=[ProblemCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("location", help="location of the problem")
    PARSER.add_argument("--name", help="alternative name for the problem")
    PARSER.add_argument("--title", help="alternative title for the problem")

    def run(self):
        install_problem(
            location=self.args.location,
            name=self.args.name,
            title=self.args.title,
        )


class UpdateProblemCommand(ProblemCommand):
    NAME = "update"
    PARSER = ArgumentParser(
        description="update an already installed problem",
        parents=[ProblemCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("name", help="name of the problem")

    def run(self):
        update_problem(name=self.args.name)


class DeleteProblemCommand(ProblemCommand):
    NAME = "delete"
    PARSER = ArgumentParser(
        description="delete a problem",
        parents=[ProblemCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("name", help="name of the problem")
    PARSER.add_argument("--yes", "-y", help="do not ask for confirmation", action="store_true")

    def run(self):
        if not self.args.yes:
            confirm = input(f"Do you really want to delete the problem {self.args.name}? (y/n) ")
            if confirm != "y":
                exit(0)
        delete_problem(name=self.args.name)


class ListProblemCommand(ProblemCommand):
    NAME = "list"
    PARSER = ArgumentParser(
        description="list installed problems",
        parents=[ProblemCommand.PARSER],
        add_help=False,
    )

    def run(self):
        problems = database.get_all_problems()
        print(tabulate(problems, headers=["Id", "Name", "Title", "Location", "Path"]))


subparsers = ProblemCommand.PARSER.add_subparsers(title="subcommand", metavar="subcommand")
subparsers.required = True
add_subparser(subparsers, InstallProblemCommand)
add_subparser(subparsers, DeleteProblemCommand)
add_subparser(subparsers, UpdateProblemCommand)
add_subparser(subparsers, ListProblemCommand)
