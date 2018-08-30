import os
import uuid
from argparse import ArgumentParser

from turingarena_cli.pack import PackBasedCommand
from turingarena_cli.remote import RemoteCommand


class LegacyDaemonCommand(PackBasedCommand):
    def _get_module_name(self):
        return "turingarena_impl.cli_server.main"

    def _get_parameters(self):
        return self.args

    def run(self):
        if self.args.command in ["skeleton", "template"]:
            self.args.what = self.args.command
            self.args.command = "make"

        if self.args.command == "make" and self.args.what != "all":
            self.args.print = True

        self.args.git_dir = self.git_dir

        if self.args.repository is None:
            self.args.send_current_dir = True

        if self.args.command not in ["evaluate", "make", "test"]:
            self.args.send_current_dir = False

        if self.args.send_current_dir:
            if not self.args.local:
                self.push_local_tree(self.working_dir_tree_id)
            self.args.tree_id = self.working_dir_tree_id
            self.args.current_dir = self.relative_current_dir
        else:
            self.args.tree_id = None
            self.args.current_dir = None

        self.args.result_file = os.path.join("/tmp", "turingarena_{}_result.json".format(str(uuid.uuid4())))

        super().run()

        if self.args.command == "make" and not self.args.print:
            self.retrieve_result(self.args.result_file)

    PARSER = ArgumentParser(
        add_help=False,
        parents=[PackBasedCommand.PARSER]
    )


INFO_PARSER = ArgumentParser(
    description="Get some info about TuringArena",
    add_help=False,
    parents=[LegacyDaemonCommand.PARSER],
)
INFO_PARSER.add_argument("what", choices=["languages"], help="what you want to know about turingarena")
INFO_PARSER.set_defaults(Command=LegacyDaemonCommand)

TEST_PARSER = ArgumentParser(
    description="Run tests",
    add_help=False,
    parents=[LegacyDaemonCommand.PARSER],
)
TEST_PARSER.add_argument("pytest_arguments", nargs="*", help="additional arguments to pass to pytest")
TEST_PARSER.set_defaults(Command=LegacyDaemonCommand)

BASE_MAKE_PARSER = ArgumentParser(
    add_help=False,
    parents=[LegacyDaemonCommand.PARSER],
)
BASE_MAKE_PARSER.add_argument(
    "--language",
    action="append",
    choices=["python", "c++", "java", "go"],
    help="which language to generate",
)
BASE_MAKE_PARSER.add_argument(
    "--print", "-p",
    action="store_true",
    help="print output to stdout instead of writing it to a file",
)
BASE_MAKE_PARSER.set_defaults(Command=LegacyDaemonCommand)

MAKE_PARSER = ArgumentParser(
    description="Generate all the necessary files for a problem",
    add_help=False,
    parents=[BASE_MAKE_PARSER],
)
MAKE_PARSER.add_argument(
    "what",
    choices=["all", "skeleton", "template", "metadata", "description"],
    default="all",
    help="what to make",
)
