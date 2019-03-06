import sys
from abc import ABC
from argparse import ArgumentParser

from tabulate import tabulate

from turingarena.driver.language import Language

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


class NewContestCommand(ContestCommand):
    NAME = "new"
    PARSER = ArgumentParser(
        description="add new contest to TuringArena",
        parents=[ContestCommand.PARSER],
        add_help=False
    )
    PARSER.add_argument("contest", help="name of the new contest")
    PARSER.add_argument("--public", "-p", help="make contest public", action="store_true")

    def run(self):
        Contest.new_contest(self.args.contest, public=self.args.public)


class DeleteContestCommand(ContestCommand):
    NAME = "delete"
    PARSER = ArgumentParser(
        description="delete contest",
        parents=[ContestCommand.PARSER],
        add_help=False
    )
    PARSER.add_argument("contest", help="name of the contest to delete")
    PARSER.add_argument("--yes", help="don't ask for confirmation", action="store_true")

    def run(self):
        if not self.args.yes:
            self.args.yes = input("Really initialize the database? (y/n)") == "y"
        if self.args.yes:
            Contest.delete_contest(self.args.contest)
        else:
            print("Abort")


class AddContestCommand(ContestCommand, ABC):
    NAME = "add"
    PARSER = ArgumentParser(
        description="Add a resource to contest",
        parents=[ContestCommand.PARSER],
        add_help=False,
    )


class RemoveContestCommand(ContestCommand, ABC):
    NAME = "remove"
    PARSER = ArgumentParser(
        description="Remove a resource to contest",
        parents=[ContestCommand.PARSER],
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
        print(tabulate(contests, headers=("Id", "Name", "Public", "Allowed languages")))


class AddUserContestCommand(AddContestCommand):
    NAME = "user"
    PARSER = ArgumentParser(
        description="add user to contest",
        parents=[AddContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("user", help="user to add to the contest")
    PARSER.add_argument("contest", help="name of the contest")

    def run(self):
        user = User.from_username(self.args.user)
        if user is None:
            print(f"No user with username {self.args.user} found!")
            exit(1)
        contest = Contest.from_name(self.args.contest)
        contest.add_user(user)


class RemoveUserContestCommand(RemoveContestCommand):
    NAME = "user"
    PARSER = ArgumentParser(
        description="remove user from contest",
        parents=[RemoveContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("user", help="user to remove from the contest")
    PARSER.add_argument("contest", help="name of the contest")

    def run(self):
        user = User.from_username(self.args.user)
        if user is None:
            print(f"No user with username {self.args.user} found!")
            exit(1)
        contest = Contest.from_name(self.args.contest)
        contest.remove_user(user)


class ListUserContestCommand(ListContestCommand):
    NAME = "users"
    PARSER = ArgumentParser(
        description="list contest users",
        parents=[ListContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("contest", help="name of the contest")

    def run(self):
        contest = Contest.from_name(self.args.contest)
        print(tabulate(contest.users, headers=("Id", "First name", "Last name", "Username", "Email", "Privilege")))


class ListProblemContestCommand(ListContestCommand):
    NAME = "problems"
    PARSER = ArgumentParser(
        description="list contest problems",
        parents=[ListContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("contest", help="name of the contest")

    def run(self):
        contest = Contest.from_name(self.args.contest)
        print(tabulate([
                (p.name, p.title)
                for p in contest.problems
            ], headers=("Name", "Title")
        ))


class AddLanguageContestCommand(AddContestCommand):
    NAME = "language"
    PARSER = ArgumentParser(
        description="add a language to a contest",
        parents=[AddContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("language", help="name of the language to add")
    PARSER.add_argument("contest", help="name of the contest")

    def run(self):
        contest = Contest.from_name(self.args.contest)
        if contest is None:
            print(f"No contest named {self.args.contest}!", file=sys.stderr)
            exit(1)

        try:
            Language.from_name(self.args.language)
        except ValueError:
            print(f"Language {self.args.language} is not currently supported by TuringArena!", file=sys.stderr)
            print(f"Currently available languages: {', '.join(lang.name for lang in Language.languages())}")
            exit(1)

        contest.add_language(self.args.language)


class RemoveLanguageContestCommand(RemoveContestCommand):
    NAME = "language"
    PARSER = ArgumentParser(
        description="add a language to a contest",
        parents=[RemoveContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("language", help="name of the language to remove")
    PARSER.add_argument("contest", help="name of the contest")

    def run(self):
        contest = Contest.from_name(self.args.contest)
        if contest is None:
            print(f"No contest named {self.args.contest}!", file=sys.stderr)
            exit(1)
        contest.remove_language(self.args.language)


class ListLanguageContestCommand(ListContestCommand):
    NAME = "languages"
    PARSER = ArgumentParser(
        description="add a language to a contest",
        parents=[ListContestCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("contest", help="name of the contest")

    def run(self):
        contest = Contest.from_name(self.args.contest)
        if contest is None:
            print(f"No contest named {self.args.contest}!", file=sys.stderr)
            exit(1)

        languages = [Language.from_name(lang) for lang in contest.allowed_languages]
        print(tabulate(((lang.name, lang.extension) for lang in languages), headers=("Name", "Extension")))


subparsers = AddContestCommand.PARSER.add_subparsers(title="subcommand", metavar="subcommand")
subparsers.required = True
add_subparser(subparsers, AddUserContestCommand)
add_subparser(subparsers, AddLanguageContestCommand)

subparsers = RemoveContestCommand.PARSER.add_subparsers(title="subcommand", metavar="subcommand")
subparsers.required = True
add_subparser(subparsers, RemoveUserContestCommand)
add_subparser(subparsers, RemoveLanguageContestCommand)

subparsers = ListContestCommand.PARSER.add_subparsers(title="subcommand", metavar="subcommand")
add_subparser(subparsers, ListUserContestCommand)
add_subparser(subparsers, ListProblemContestCommand)
add_subparser(subparsers, ListLanguageContestCommand)

subparsers = ContestCommand.PARSER.add_subparsers(title="subcommand", metavar="subcommand")
subparsers.required = True
add_subparser(subparsers, NewContestCommand)
add_subparser(subparsers, DeleteContestCommand)
add_subparser(subparsers, ListContestCommand)
add_subparser(subparsers, AddContestCommand)
add_subparser(subparsers, RemoveContestCommand)
