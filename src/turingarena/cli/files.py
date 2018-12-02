import logging
import os
import sys
from argparse import ArgumentParser

from turingarena.cli.base import BASE_PARSER
from turingarena.cli.command import Command
from turingarena.file.generated import PackGeneratedDirectory


class FileCommand(Command):
    PARSER = ArgumentParser(
        description="Get generated files",
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


class FileSyncCommand(FileCommand):
    PARSER = ArgumentParser(
        description="Copy all generated files",
        parents=[FileCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("output", help="Output folder")

    def run(self):
        directory = PackGeneratedDirectory(".")

        output = self.args.output
        os.mkdir(output)
        for path, g in directory.targets:
            fullpath = os.path.join(output, path)
            logging.info(f"Creating file '{fullpath}'")
            os.makedirs(os.path.dirname(fullpath), exist_ok=True)
            with open(fullpath, "x") as f:
                g(f)


subparsers = FileCommand.PARSER.add_subparsers(title="subcommand", dest="subcommand")
subparsers.required = True
subparsers.add_parser(
    "cat",
    parents=[FileCatCommand.PARSER, BASE_PARSER],
    help=FileCatCommand.PARSER.description,
).set_defaults(Command=FileCatCommand)
subparsers.add_parser(
    "sync",
    parents=[FileSyncCommand.PARSER, BASE_PARSER],
    help=FileSyncCommand.PARSER.description,
).set_defaults(Command=FileSyncCommand)
