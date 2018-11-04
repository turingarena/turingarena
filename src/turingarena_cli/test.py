from argparse import ArgumentParser

from turingarena_cli.pack import PackBasedCommand
from turingarena_cli.remote import RemotePythonCommand
from turingarena_common.commands import TestCommandParameters


class TestCommand(RemotePythonCommand, PackBasedCommand):
    def _get_command_parameters(self):
        return TestCommandParameters(
            pytest_arguments=self.args.pytest_arguments,
            working_directory=self.working_directory,
        )

    PARSER = ArgumentParser(
        description="Run tests",
        add_help=False,
        parents=[PackBasedCommand.PARSER],
    )
    PARSER.add_argument("pytest_arguments", nargs="*", help="additional arguments to pass to pytest")


TestCommand.PARSER.set_defaults(Command=TestCommand)
