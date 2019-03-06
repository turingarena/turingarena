import logging
import os
import shutil
import sys

from abc import ABC
from argparse import ArgumentParser

from turingarena.cli.command import Command, add_subparser
from turingarena.file.generated import PackGeneratedDirectory


class FileCommand(Command, ABC):
    PARSER = ArgumentParser(
        description="Get generated files",
        add_help=False,
    )


class FileListCommand(FileCommand):
    NAME = "list"
    PARSER = ArgumentParser(
        description="List the available files in the current directory",
        parents=[FileCommand.PARSER],
        add_help=False,
    )

    def run(self):
        directory = PackGeneratedDirectory(".")
        for path, _ in directory.targets:
            print(path)


class FileCatCommand(FileCommand):
    NAME = "cat"
    PARSER = ArgumentParser(
        description="Print the content of a file to stdout",
        parents=[FileCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("path", help="Path to the file to print")

    def run(self):
        PackGeneratedDirectory(".").cat_file(self.args.path, file=sys.stdout)


class FileSyncCommand(FileCommand):
    NAME = "sync"
    PARSER = ArgumentParser(
        description="Copy all generated files",
        parents=[FileCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("output", help="Output folder", nargs="?", default="turingarena-files/")
    PARSER.add_argument("--force", "-f", help="Remove output folder before sync", action="store_true")
    PARSER.add_argument("--zip", "-z", help="create a Zip archive with the files", action="store_true")

    def run(self):
        output = self.args.output
        if self.args.force:
            shutil.rmtree(output, ignore_errors=True)

        directory = PackGeneratedDirectory(".")

        try:
            os.mkdir(output)
        except FileExistsError:
            print("output directory already exists: use --force to overwrite")
            exit(1)
        for path, g in directory.targets:
            fullpath = os.path.join(output, path)
            logging.info(f"Creating file '{fullpath}'")
            os.makedirs(os.path.dirname(fullpath), exist_ok=True)
            with open(fullpath, "x") as f:
                g(f)

        if self.args.zip:
            shutil.make_archive("files", "zip", self.args.output)


subparsers = FileCommand.PARSER.add_subparsers(title="subcommand", dest="subcommand")
subparsers.required = True
add_subparser(subparsers, FileCatCommand)
add_subparser(subparsers, FileSyncCommand)
add_subparser(subparsers, FileListCommand)
