import os
import sys
import base64

from abc import ABC
from argparse import ArgumentParser
from functools import lru_cache

from turingarena.cli.command import Command
from turingarena.evaluation.events import EvaluationEventType
from turingarena.evaluation.evaluator import Evaluator


class SubmissionCommand(Command, ABC):
    PARSER = ArgumentParser(
        add_help=False,
    )
    PARSER.add_argument("file", help="submission file", nargs="+")

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

    def _parse_file(self, argument, default_fields):
        if ":" in argument:
            name, path = argument.split(":", 1)
        else:
            name, path = next(default_fields), argument

        if not os.path.exists(path):
            print(f"ERROR: file `{path}` does not exist!")
            exit(1)
        return name, path


class EvaluateCommand(SubmissionCommand):
    PARSER = ArgumentParser(
        add_help=False,
        description="Evaluate a submission",
        parents=[SubmissionCommand.PARSER]
    )
    PARSER.add_argument("--events", help="show evaluation events as JSON Lines", action="store_true")
    PARSER.add_argument("--store-files", help="stores files produced by the evaluator", action="store_true")
    PARSER.add_argument("--seed", help="set random seed", type=int)

    def _do_evaluate(self):
        return Evaluator().evaluate(
            self.submission,
            seed=self.args.seed,
        )

    def run(self):
        files_dir = os.path.join(os.getcwd(), "generated-files")
        if self.args.store_files:
            os.makedirs(files_dir, exist_ok=True)
        for event in self._do_evaluate():
            if self.args.store_files and event.type is EvaluationEventType.FILE:
                with open(os.path.join(files_dir, event.payload["filename"]), "wb") as f:
                    f.write(base64.standard_b64decode(event.payload["content_base64"]))
            if self.args.events:
                print(event)
            else:
                if event.type is EvaluationEventType.TEXT:
                    sys.stdout.write(event.payload)


EvaluateCommand.PARSER.set_defaults(Command=EvaluateCommand)
