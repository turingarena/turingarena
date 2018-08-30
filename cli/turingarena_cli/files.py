from turingarena_cli.pack import PackBasedCommand
from turingarena_cli.remote import RemoteCommand
from turingarena_common.commands import FileCommandParameters, FileCatCommandParameters


class FileCatCommand(RemoteCommand, PackBasedCommand):
    def _get_command_parameters(self):
        return FileCommandParameters(
            working_directory=self.working_directory,
            command=FileCatCommandParameters(
                path=self.args.path,
            ),
        )


def create_file_parser(subparsers):
    parser = subparsers.add_parser("file", help="Get TuringArena generated files")
    subparsers2 = parser.add_subparsers(dest="subcommand")
    create_file_cat_parser(subparsers2)


def create_file_cat_parser(subparsers):
    parser = subparsers.add_parser("cat", help="Print the content of a file to stdout")
    parser.add_argument("path", help="Path to the file to print")
    parser.set_defaults(Command=FileCatCommand)
