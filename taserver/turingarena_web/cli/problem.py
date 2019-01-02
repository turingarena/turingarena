import sys
from abc import ABC
from argparse import ArgumentParser

from tabulate import tabulate
from turingarena_web.model.problem import Problem
from turingarena_web.cli.base import BASE_PARSER
from turingarena_web.cli.command import Command, add_subparser


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
        Problem.install(
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
        problem = Problem.from_name(name=self.args.name)
        problem.update()


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
        problem = Problem.from_name(name=self.args.name)
        if problem is None:
            print(f"No problem named {self.args.name} found!", file=sys.stderr)
            exit(1)
        if not self.args.yes:
            confirm = input(f"Do you really want to delete the problem {self.args.name}? (y/n) ")
            if confirm != "y":
                exit(0)
        problem.delete()


class ListProblemCommand(ProblemCommand):
    NAME = "list"
    PARSER = ArgumentParser(
        description="list installed problems",
        parents=[ProblemCommand.PARSER],
        add_help=False,
    )

    def run(self):
        print(tabulate(Problem.problems(), headers=["Id", "Name", "Title", "Location"]))


subparsers = ProblemCommand.PARSER.add_subparsers(title="subcommand", metavar="subcommand")
subparsers.required = True
add_subparser(subparsers, InstallProblemCommand)
add_subparser(subparsers, DeleteProblemCommand)
add_subparser(subparsers, UpdateProblemCommand)
add_subparser(subparsers, ListProblemCommand)
