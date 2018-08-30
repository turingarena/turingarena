import os
import uuid

from turingarena_cli.pack import PackBasedCommand


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
                self.push_local_tree(self.local_tree_id)
            self.args.tree_id = self.local_tree_id
            self.args.current_dir = self.relative_current_dir
        else:
            self.args.tree_id = None
            self.args.current_dir = None

        self.args.result_file = os.path.join("/tmp", "turingarena_{}_result.json".format(str(uuid.uuid4())))

        super().run()

        if self.args.command == "make" and not self.args.print:
            self.retrieve_result(self.args.result_file)


def create_info_parser(subparsers):
    parser = subparsers.add_parser("info", help="get some info about TuringArena")
    parser.add_argument("what", choices=["languages"], help="what you want to know about turingarena")
    parser.set_defaults(Command=LegacyDaemonCommand)


def create_make_parser(parser, alias=False):
    if not alias:
        parser.add_argument("what", help="what to make", default="all",
                            choices=["all", "skeleton", "template", "metadata", "description"])
    parser.add_argument("--language", "-l", help="which language to generate", action="append",
                        choices=["python", "c++", "java", "go"])
    parser.add_argument("--print", "-p", help="Print output to stdout instead of writing it to a file",
                        action="store_true")
    parser.set_defaults(Command=LegacyDaemonCommand)


def create_test_parser(subparsers):
    parser = subparsers.add_parser("test", help="execute tests")
    parser.add_argument("pytest_arguments", nargs="*", help="additional arguments to pass to pytest")
    parser.set_defaults(Command=LegacyDaemonCommand)