from turingarena_cli.pack import PackBasedCommand
from turingarena_cli.remote import RemoteCommand
from turingarena_common.commands import EvaluateCommandParameters


class EvaluateCommand(RemoteCommand, PackBasedCommand):
    def _get_command_parameters(self):
        return EvaluateCommandParameters(
            working_directory=self.working_directory,
            evaluator=self.args.evaluator,
            file=self.args.file,
            raw_output=self.args.raw,
        )


def create_evaluate_parser(subparsers):
    parser = subparsers.add_parser("evaluate", help="Evaluate a submission")
    parser.add_argument("file", help="submission file", nargs="+")
    parser.add_argument("--evaluator", "-e", help="evaluator program", default="evaluator.py")
    parser.add_argument("--raw", "-r", help="use raw output", action="store_true")

    parser.set_defaults(Command=EvaluateCommand)