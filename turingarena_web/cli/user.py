from abc import ABC
from argparse import ArgumentParser
from tabulate import tabulate

from turingarena_web.cli.base import BASE_PARSER
from turingarena_web.cli.command import Command, add_subparser
from turingarena_web.database import database


class UserCommand(Command, ABC):
    NAME = "user"
    PARSER = ArgumentParser(
        description="Manipulate TuringArena user",
        parents=[BASE_PARSER],
        add_help=False,
    )


class AddUserCommand(UserCommand):
    NAME = "add"
    PARSER = ArgumentParser(
        description="Add a new user",
        parents=[UserCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("username", help="username for the user to add")
    PARSER.add_argument("--first-name", "-f", help="user first name")
    PARSER.add_argument("--last-name", "-l", help="user last name")
    PARSER.add_argument("--email", "-e", help="user email")
    PARSER.add_argument("--password", "-p", help="user password")
    PARSER.add_argument("--yes", "-y", help="do not ask for confirmation", action="store_true")

    def run(self):
        print(f"Creating user {self.args.username}")
        if self.args.first_name is None:
            self.args.first_name = input("First name: ")
        if self.args.last_name is None:
            self.args.last_name = input("Last name: ")
        if self.args.email is None:
            self.args.email = input("Email: ")
        if self.args.password is None:
            self.args.password = input("Password (min 8 char): ")
        if not self.args.yes:
            confirm = input("Is the data inserted correct? (y/n)")
            if confirm != "y":
                exit(0)
        database.insert_user(
            username=self.args.username,
            first_name=self.args.first_name,
            last_name=self.args.last_name,
            email=self.args.email,
            password=self.args.password,
        )


class SetUserPrivilegeCommand(UserCommand):
    NAME = "privilege"
    PARSER = ArgumentParser(
        description="set privilege of a user",
        parents=[UserCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("user", help="user for changing privilege to")
    PARSER.add_argument("privilege", help="privilege level for user", choices=["STANDARD", "TUTOR", "ADMIN"])
    PARSER.add_argument("--yes", "-y", help="do not ask for confirmation", action="store_true")

    def run(self):
        if not self.args.yes:
            confirm = input(f"Setting privilege of user {self.args.user} to {self.args.privilege}. Confirm? (y/n) ")
            if confirm != "y":
                exit(0)
        database.set_user_privilete(
            user=self.args.user,
            privilege=self.args.privilege,
        )


class DeleteUserCommand(UserCommand):
    NAME = "delete"
    PARSER = ArgumentParser(
        description="delete a user",
        parents=[UserCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("username", help="username of the user to delete")
    PARSER.add_argument("--yes", "-y", help="do not ask for confirmation", action="store_true")

    def run(self):
        if not self.args.yes:
            confirm = input(f"Really delete user {self.args.username}? (y/n) ")
            if confirm != "y":
                exit(0)
        database.delete_user(username=self.args.username)


class ImportUserCommand(UserCommand):
    NAME = "import"
    PARSER = ArgumentParser(
        description="import users from a CMS-like yaml file",
        parents=[UserCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("filename")

    def run(self):
        raise NotImplementedError("this command will be implemented in a future release")


class ListUserCommand(UserCommand):
    NAME = "list"
    PARSER = ArgumentParser(
        description="list present users",
        parents=[UserCommand.PARSER],
        add_help=False,
    )

    def run(self):
        users = database.get_users()
        print(tabulate(users, headers=["Id", "First name", "Last name", "Username", "Email", "Privilege"]))


subparsers = UserCommand.PARSER.add_subparsers(title="subcommand", metavar="subcommand")
subparsers.required = True
add_subparser(subparsers, AddUserCommand)
add_subparser(subparsers, DeleteUserCommand)
add_subparser(subparsers, ImportUserCommand)
add_subparser(subparsers, ListUserCommand)
