import re

from turingarena_impl.cli import docopt_cli
from turingarena_impl.evaluation.python import PythonEvaluator
from turingarena_impl.evaluation.submission import SubmissionField, SubmissionFieldType

PREFIX_REGEX = re.compile(r"^[a-z][a-z0-9_]*=([sf]?[@+])?")


@docopt_cli
def evaluate_cli(args):
    # FIXME: drop docopt, use argparse
    """Evaluates a submission.

    Usage:
        evaluate [options] [] [-F <f>]... [-S <s>]... <files> ...

    Options:
        -e --evaluator=<id>  Evaluator [default: ./evaluate.py]

        -F --file=<field>  Specifies a submission field.
        --file-as-string=<field>  Specifies a submission field.
        -S --string=<field>  Specifies a submission field.
        --string-as-file=<field>  Specifies a submission field.

    """

    for i, f in enumerate_files(args["<files>"]):
        args["--file"].append(f"source{i}={f}")

    submission = dict(get_submission_fields(args))

    evaluation = PythonEvaluator(args["--evaluator"]).evaluate(submission)

    for event in evaluation:
        print(event)


def enumerate_files(files):
    if len(files) == 1:
        yield "", files[0]
    else:
        for i, f in enumerate(files):
            yield str(i), f


def get_submission_fields(args):
    for option_name, in_type, out_type in (
            ("--file", "file", "file"),
            # ("--file-as-string", "file", "string"),
            ("--string", "string", "string"),
            # ("--string-as-file", "string", "file"),
    ):
        for arg in args[option_name]:
            name, value = arg.split("=", 1)
            yield name, make_field(out_type, value)


def make_field(t, value):
    return SubmissionField(SubmissionFieldType(t), value)
