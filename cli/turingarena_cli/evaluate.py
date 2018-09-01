import os
from argparse import ArgumentParser
from functools import lru_cache

from turingarena_cli.pack import PackBasedCommand
from turingarena_cli.remote import RemotePythonCommand
from turingarena_common.commands import EvaluateCommandParameters
from turingarena_common.submission import SubmissionFile


class EvaluateCommand(PackBasedCommand, RemotePythonCommand):
    def _get_command_parameters(self):
        return EvaluateCommandParameters(
            working_directory=self.working_directory,
            evaluator=self.args.evaluator,
            submission=self.submission,
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

    @property
    def default_fields(self):
        return ["source"]

    @property
    @lru_cache(None)
    def submission(self):
        default_fields = iter(self.default_fields)
        return dict(
            self._parse_file(arg, default_fields)
            for arg in self.args.file
        )

    def _load_file(self, path):
        filename = os.path.basename(path)
        with open(path, "rb") as f:
            content = f.read()
        return filename, content

    def _parse_file(self, argument, default_fields):
        if ":" in argument:
            name, path = argument.split(":", 1)
            filename, content = self._load_file(path)
        elif "=" in argument:
            name, text_content = argument.split("=", 1)
            content = text_content.encode()
            filename = name + ".txt"
        else:
            path = argument
            name = next(default_fields)
            filename, content = self._load_file(path)
        return name, SubmissionFile(
            filename=filename,
            content=content,
        )


EvaluateCommand.PARSER.set_defaults(Command=EvaluateCommand)
