import sys
from abc import ABC
from argparse import ArgumentParser
from tabulate import tabulate

from turingarena_web.cli.base import BASE_PARSER
from turingarena_web.cli.command import Command, add_subparser
from turingarena_web.model.user import User, UserPrivilege


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
        print(f"Creating user with username: {self.args.username}")
        if User.from_username(self.args.username) is not None:
            print(f"A user with username '{self.args.username}' already exists!", file=sys.stderr)
            exit(1)
        if self.args.first_name is None:
            self.args.first_name = input("First name: ")
        else:
            print(f"First name: {self.args.first_name}")
        if self.args.last_name is None:
            self.args.last_name = input("Last name: ")
        else:
            print(f"Last name: {self.args.last_name}")
        if self.args.email is None:
            self.args.email = input("Email: ")
        else:
            print(f"Email: {self.args.email}")
        if self.args.password is None:
            self.args.password = input("Password (min 8 char): ")
        else:
            print(f"Password: {self.args.password}")
        if not self.args.yes:
            confirm = input("Is the data inserted correct? (y/n)")
            if confirm != "y":
                exit(0)
        if User.insert(
            username=self.args.username,
            first_name=self.args.first_name,
            last_name=self.args.last_name,
            email=self.args.email,
            password=self.args.password,
        ) is None:
            print("There was an error inserting the user into the system")
        else:
            print(f"The user {self.args.username} was correctly inserted in the system")


class SetUserPrivilegeCommand(UserCommand):
    NAME = "privilege"
    PARSER = ArgumentParser(
        description="set privilege of a user",
        parents=[UserCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("username", help="user for changing privilege to")
    PARSER.add_argument("privilege", help="privilege level for user", choices=["STANDARD", "TUTOR", "ADMIN"])
    PARSER.add_argument("--yes", "-y", help="do not ask for confirmation", action="store_true")

    def run(self):
        user = User.from_username(self.args.username)
        if user is None:
            print(f"No user with username '{self.args.username}' exists!", file=sys.stderr)
            exit(1)
        if not self.args.yes:
            confirm = input(f"Setting privilege of user {self.args.username} to {self.args.privilege}. Confirm? (y/n) ")
            if confirm != "y":
                exit(0)
        user.set_privilege(UserPrivilege(self.args.privilege))


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
        user = User.from_username(self.args.username)
        if user is None:
            print(f"No user with username '{self.args.username}' exists!", file=sys.stderr)
            exit(1)
        if not self.args.yes:
            confirm = input(f"Really delete user {self.args.username}? (y/n) ")
            if confirm != "y":
                exit(0)
        user.delete()


class ListUserCommand(UserCommand):
    NAME = "list"
    PARSER = ArgumentParser(
        description="list present users",
        parents=[UserCommand.PARSER],
        add_help=False,
    )

    def run(self):
        print(tabulate(User.users(), headers=["Id", "First name", "Last name", "Username", "Email", "Password", "Privilege"]))


subparsers = UserCommand.PARSER.add_subparsers(title="subcommand", metavar="subcommand")
subparsers.required = True
add_subparser(subparsers, AddUserCommand)
add_subparser(subparsers, DeleteUserCommand)
add_subparser(subparsers, ListUserCommand)
add_subparser(subparsers, SetUserPrivilegeCommand)
