from argparse import ArgumentParser

from turingarena_cli.base import BASE_PARSER
from turingarena_cli.pack import PackBasedCommand
from turingarena_cli.remote import RemotePythonCommand
from turingarena_common.commands import EvaluateCommandParameters


class EvaluateCommand(PackBasedCommand, RemotePythonCommand):
    def _get_command_parameters(self):
        return EvaluateCommandParameters(
            working_directory=self.working_directory,
            evaluator=self.args.evaluator,
            file=self.args.file,
            raw_output=self.args.raw,
        )

    PARSER = ArgumentParser(
        add_help=False,
        description="Evaluate a submission",
        parents=[PackBasedCommand.PARSER]
    )
    PARSER.add_argument("file", help="submission file", nargs="+")
    PARSER.add_argument("--evaluator", "-e", help="evaluator program", default="evaluator.py")
    PARSER.add_argument("--raw", "-r", help="use raw output", action="store_true")


EvaluateCommand.PARSER.set_defaults(Command=EvaluateCommand)
