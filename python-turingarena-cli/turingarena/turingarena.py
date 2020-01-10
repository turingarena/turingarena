import argparse
import yaml

from os import path
from turingarena.contest import Contest
from turingarena.graphql import GraphQlClient
from turingarena.submission import SubmissionFile

DEFAULT_SERVER = "http://localhost:8080"

parser = argparse.ArgumentParser(description="TuringArena CLI administration client")
parser.add_argument("-s", "--server", help="address of TuringArena", default=DEFAULT_SERVER)
parser.add_argument("-c", "--contest", help="contest to modify", default="default")

subparsers = parser.add_subparsers(dest="command", description="command to run")
subparsers.required = True

init_db_parser = subparsers.add_parser("init-db", help="initialize the database")

show_parser = subparsers.add_parser("show", help="show current contest")

import_parser = subparsers.add_parser("import", help="import a contest")
import_parser.add_argument("-p", "--path", help="path of the contest to import", default=".")
import_parser.add_argument("-f", "--fresh", help="reimport the contest from scratch", default=False)

export_parser = subparsers.add_parser("export", help="export the contest submissions")
export_parser.add_argument("-p", "--path", help="path where to export to", default=".")

convert_parser = subparsers.add_parser("convert", help="convert a ItalyYAML contest to a TuringArena contest")
convert_parser.add_argument("-p", "--path", help="path of the contest to convert", default=".")

submit_parser = subparsers.add_parser("submit", help="create a new submission")
submit_parser.add_argument("user", help="user for the submission")
submit_parser.add_argument("problem", help="problem to submit to")
submit_parser.add_argument("file", help="file to submit")


class TuringArena:
    client: GraphQlClient
    args: argparse.Namespace

    def __init__(self):
        self.args = parser.parse_args()
        self.client = GraphQlClient(self.args.server)

    @property
    def path(self) -> str:
        return path.abspath(self.args.path)

    def run_init_db(self):
        print(self.client.init_db())

    def run_import(self):
        contest = Contest.from_directory(self.path)
        print(self.client.create_contest(dict(
            contest=contest.to_graphql(),
            problems=list(map(lambda p: p.to_graphql(), contest.problems)),
            users=list(map(lambda u: u.to_graphql(), contest.users)),
        )))

    def run_show(self):
        print(self.client.show_contest())

    def run_export(self):
        submissions = map(lambda s: s.from_graphql(), self.client.submissions())
        for submission in submissions:
            submission.write(path.join(self.path, "submissions"))

    def run_convert(self):
        contest = Contest.from_italy_yaml(self.path)
        with open(path.join(self.path, "turingarena.yaml"), "w") as f:
            yaml.safe_dump(contest.to_turingarena_yaml(), f)

    def run_submit(self):
        self.client.submit(
            user=self.args.user,
            problem=self.args.problem,
            files=[SubmissionFile.from_file(self.args.file)]
        )

    def run(self):
        getattr(self, "run_" + self.args.command.replace("-", "_"))()


def main():
    TuringArena().run()
