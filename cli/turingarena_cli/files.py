from abc import abstractmethod
from argparse import ArgumentParser

from turingarena_cli.pack import PackBasedCommand
from turingarena_common.commands import FileCommandParameters, FileCatCommandParameters


class FileCommand(PackBasedCommand):
    @abstractmethod
    def _get_file_command_parameters(self):
        pass

    def _get_command_parameters(self):
        return FileCommandParameters(
            working_directory=self.working_directory,
            command=self._get_file_command_parameters(),
        )

    PARSER = ArgumentParser(
        description="Get generated files",
        parents=[PackBasedCommand.PARSER],
        add_help=False,
    )


class FileCatCommand(FileCommand):
    def _get_file_command_parameters(self):
        return FileCatCommandParameters(
            path=self.args.path,
        )

    PARSER = ArgumentParser(
        description="Print the content of a file to stdout",
        parents=[FileCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("path", help="Path to the file to print")


FILE_PARSER = ArgumentParser(add_help=False)

subparsers = FILE_PARSER.add_subparsers(title="subcommand", dest="subcommand")
subparsers.required = True
subparsers.add_parser(
    "cat",
    parents=[FileCatCommand.PARSER],
    help=FileCatCommand.PARSER.description,
).set_defaults(Command=FileCatCommand)
