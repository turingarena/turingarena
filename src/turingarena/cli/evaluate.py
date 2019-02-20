import os
import sys

from abc import ABC
from argparse import ArgumentParser
from functools import lru_cache

from turingarena.cli.command import Command
from turingarena.evaluation.events import EvaluationEventType
from turingarena.evaluation.evaluator import Evaluator
from turingarena.evaluation.submission import SubmissionFile


class SubmissionCommand(Command, ABC):
    PARSER = ArgumentParser(
        add_help=False,
    )
    PARSER.add_argument("file", help="submission file", nargs="+")

    @property
    def default_fields(self):
        return ["source"]

    def _should_load_submission_files(self):
        """
        Override and return True to load file content in memory,
        to use with remote services.
        """
        return False

    @property
    @lru_cache(None)
    def submission(self):
        default_fields = iter(self.default_fields)
        return dict(
            self._parse_file(arg, default_fields)
            for arg in self.args.file
        )

    def _load_file(self, path):
        if not self._should_load_submission_files():
            return path

        filename = os.path.basename(path)
        with open(path, "rb") as f:
            content = f.read()
        return SubmissionFile(filename=filename, content=content)

    def _parse_file(self, argument, default_fields):
        if ":" in argument:
            name, path = argument.split(":", 1)
            return name, self._load_file(path)

        if self._should_load_submission_files() and "=" in argument:
            name, text_content = argument.split("=", 1)
            return name, SubmissionFile(
                filename=name + ".txt",
                content=text_content.encode(),
            )

        name = next(default_fields)
        path = argument
        return name, self._load_file(path)


class EvaluateCommand(SubmissionCommand):
    PARSER = ArgumentParser(
        add_help=False,
        description="Evaluate a submission",
        parents=[SubmissionCommand.PARSER]
    )
    PARSER.add_argument("--events", help="show evaluation events as JSON Lines", action="store_true")
    PARSER.add_argument("--seed", help="set random seed", type=int)

    def _do_evaluate(self):
        return Evaluator().evaluate(
            self.submission,
            seed=self.args.seed,
        )

    def run(self):
        for event in self._do_evaluate():
            if self.args.events:
                print(event)
            else:
                if event.type is EvaluationEventType.TEXT:
                    sys.stdout.write(event.payload)


EvaluateCommand.PARSER.set_defaults(Command=EvaluateCommand)
