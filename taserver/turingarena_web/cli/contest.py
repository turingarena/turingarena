from abc import ABC
from argparse import ArgumentParser

from tabulate import tabulate

from turingarena_web.cli.base import BASE_PARSER
from turingarena_web.cli.command import Command, add_subparser
from turingarena_web.model.contest import Contest
from turingarena_web.model.user import User


class ContestCommand(Command, ABC):
    NAME = "contest"
    PARSER = ArgumentParser(
        description="manipulate a TuringArena contest",
        parents=[BASE_PARSER],
        add_help=False,
    )


class ListContestCommand(ContestCommand):
    NAME = "list"
    PARSER = ArgumentParser(
        description="list available contests",
        parents=[ContestCommand.PARSER],
        add_help=False,
    )

    def run(self):
        contests = Contest.contests()
        print(tabulate(contests, headers=("Name",)))


class AddUserContestCommand(ContestCommand):
    NAME = "add_user"
    PARSER = ArgumentParser(
        description="add user to contest",
        parents=[ContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("user", help="user to add to the contest")
    PARSER.add_argument("contest", help="name of the contest")

    def run(self):
        user = User.from_username(self.args.user)
        if user is None:
            print(f"No user with username {self.args.user} found!")
            exit(1)
        contest = Contest.contest(self.args.contest)
        if contest is None:
            print(f"No contest named {contest.name} found!")
            exit(1)
        user.add_to_contest(contest)


class RemoveUserContestCommand(ContestCommand):
    NAME = "remove_user"
    PARSER = ArgumentParser(
        description="remove user from contest",
        parents=[ContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("user", help="user to remove from the contest")
    PARSER.add_argument("contest", help="name of the contest")

    def run(self):
        user = User.from_username(self.args.user)
        if user is None:
            print(f"No user with username {self.args.user} found!")
            exit(1)
        contest = Contest.contest(self.args.contest)
        user.remove_from_contest(contest)


class ListUserContestCommand(ContestCommand):
    NAME = "list_users"
    PARSER = ArgumentParser(
        description="list contest users",
        parents=[ContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("contest", help="name of the contest")

    def run(self):
        contest = Contest.contest(self.args.contest)
        print(tabulate(contest.users, headers=("Id", "First name", "Last name", "Username", "Email", "Privilege")))


subparsers = ContestCommand.PARSER.add_subparsers()
subparsers.required = True
add_subparser(subparsers, ListContestCommand)
add_subparser(subparsers, AddUserContestCommand)
add_subparser(subparsers, RemoveUserContestCommand)
