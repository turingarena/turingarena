from abc import ABC
from argparse import ArgumentParser

from tabulate import tabulate
from turingarena_web.cli.base import BASE_PARSER
from turingarena_web.cli.command import Command, add_subparser
from turingarena_web.model.contest import Contest


class ContestCommand(Command, ABC):
    NAME = "contest"
    PARSER = ArgumentParser(
        description="manipulate a TuringArena contest",
        parents=[BASE_PARSER],
        add_help=False,
    )


class AddContestCommand(ContestCommand):
    NAME = "new"
    PARSER = ArgumentParser(
        description="add new contest to TuringArena",
        parents=[ContestCommand.PARSER],
        add_help=False
    )
    PARSER.add_argument("name", help="name of the new contest")

    def run(self):
        Contest.new_contest(self.args.name)


class DeleteContestCommand(ContestCommand):
    NAME = "delete"
    PARSER = ArgumentParser(
        description="delete contest",
        parents=[ContestCommand.PARSER],
        add_help=False
    )
    PARSER.add_argument("name", help="name of the contest to delete")

    def run(self):
        Contest.delete_contest(self.args.name)


class ListContestCommand (ContestCommand):
    NAME = "list"
    PARSER = ArgumentParser(
        description="list available contests",
        parents=[ContestCommand.PARSER],
        add_help=False,
    )

    def run(self):
        contests = Contest.contests()
        print(tabulate(contests, headers=["Id", "Name", "Public", "Allowed languages"]))


class UserContestCommand(ContestCommand, ABC):
    NAME = "user"
    PARSER = ArgumentParser(
        description="manipulate contest users",
        parents=[ContestCommand.PARSER],
        add_help=False,
    )


class AddUserContestCommand(UserContestCommand):
    NAME = "add"
    PARSER = ArgumentParser(
        description="add user to contest",
        parents=[UserContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("contest", help="name of the contest")
    PARSER.add_argument("user", help="user to add to the contest")

    def run(self):
        contest = Contest.from_name(self.args.contest)
        contest.add_user(self.args.user)


class RemoveUserContestCommand(UserContestCommand):
    NAME = "remove"
    PARSER = ArgumentParser(
        description="remove user from contest",
        parents=[UserContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("contest", help="name of the contest")
    PARSER.add_argument("user", help="user to remove from the contest")

    def run(self):
        contest = Contest.from_name(self.args.contest)
        contest.remove_user(self.args.user)


class ListUserContestCommand(UserContestCommand):
    NAME = "list"
    PARSER = ArgumentParser(
        description="list contest users",
        parents=[UserContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("contest", help="name of the contest")

    def run(self):
        contest = Contest.from_name(self.args.contest)
        print(tabulate(contest.users, headers=["Id", "First name", "Last name", "Username", "Email", "Privilege"]))


subparsers = UserContestCommand.PARSER.add_subparsers(title="subcommand", metavar="subcommand")
subparsers.required = True
add_subparser(subparsers, AddUserContestCommand)
add_subparser(subparsers, RemoveUserContestCommand)
add_subparser(subparsers, ListUserContestCommand)


class ProblemContestCommand(ContestCommand, ABC):
    NAME = "problem"
    PARSER = ArgumentParser(
        description="manipulate contest problems",
        parents=[ContestCommand.PARSER],
        add_help=False,
    )


class AddProblemContestCommand(ProblemContestCommand):
    NAME = "add"
    PARSER = ArgumentParser(
        description="add problem to contest",
        parents=[ProblemContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("contest", help="name of the contest")
    PARSER.add_argument("problem", help="problem to add to the contest")

    def run(self):
        contest = Contest.from_name(self.args.contest)
        contest.add_problem(self.args.problem)


class RemoveProblemContestCommand(ProblemContestCommand):
    NAME = "remove"
    PARSER = ArgumentParser(
        description="remove problem from contest",
        parents=[ProblemContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("contest", help="name of the contest")
    PARSER.add_argument("problem", help="problem to remove from the contest")

    def run(self):
        contest = Contest.from_name(self.args.contest)
        contest.remove_problem(self.args.problem)


class ListProblemContestCommand(ProblemContestCommand):
    NAME = "list"
    PARSER = ArgumentParser(
        description="list contest problems",
        parents=[ProblemContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("contest", help="name of the contest")

    def run(self):
        contest = Contest.from_name(self.args.contest)
        print(tabulate(contest.problems, headers=["Id", "Name", "Title", "Location", "Path"]))


subparsers = ProblemContestCommand.PARSER.add_subparsers(title="subcommand", metavar="subcommand")
subparsers.required = True
add_subparser(subparsers, AddProblemContestCommand)
add_subparser(subparsers, RemoveProblemContestCommand)
add_subparser(subparsers, ListProblemContestCommand)

subparsers = ContestCommand.PARSER.add_subparsers(title="subcommand", metavar="subcommand")
subparsers.required = True
add_subparser(subparsers, AddContestCommand)
add_subparser(subparsers, DeleteContestCommand)
add_subparser(subparsers, ListContestCommand)
add_subparser(subparsers, UserContestCommand)
add_subparser(subparsers, ProblemContestCommand)
