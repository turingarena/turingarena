import sys
from argparse import ArgumentParser

from turingarena_cli.command import Command
from turingarena_cli.pack import PackBasedCommand
from turingarena_impl.file.generated import PackGeneratedDirectory


class FileCommand(Command):
    PARSER = ArgumentParser(
        description="Get generated files",
        parents=[PackBasedCommand.PARSER],
        add_help=False,
    )


class FileCatCommand(FileCommand):
    PARSER = ArgumentParser(
        description="Print the content of a file to stdout",
        parents=[FileCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("path", help="Path to the file to print")

    def run(self):
        PackGeneratedDirectory(".").cat_file(self.args.path, file=sys.stdout)


subparsers = FileCommand.PARSER.add_subparsers(title="subcommand", dest="subcommand")
subparsers.required = True
subparsers.add_parser(
    "cat",
    parents=[FileCatCommand.PARSER],
    help=FileCatCommand.PARSER.description,
).set_defaults(Command=FileCatCommand)
