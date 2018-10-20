import sys
from argparse import ArgumentParser

from turingarena_cli.pack import PackBasedCommand


class LegacyDaemonCommand(PackBasedCommand):
    def _get_module_name(self):
        return "turingarena_impl.cli_server.main"

    def _get_parameters(self):
        return self.args

    def run(self):
        print(f"WARNING: The command 'turingarena {self.args.command}' is deprecated and will be removed in the future.", file=sys.stderr)
        print("Use the new command 'turingarena file cat' instead", file=sys.stderr)

        if "what" not in self.args:
            self.args.what = self.args.command

        self.args.git_dir = self.git_dir

        if self.args.repository is None:
            self.args.send_current_dir = True

        if self.args.send_current_dir:
            if not self.args.local:
                self.push_local_tree(self.working_dir_tree_id)
            self.args.tree_id = self.working_dir_tree_id
            self.args.current_dir = self.relative_current_dir
        else:
            self.args.tree_id = None
            self.args.current_dir = None

        super(LegacyDaemonCommand, self).run()

    PARSER = ArgumentParser(
        add_help=False,
        parents=[PackBasedCommand.PARSER]
    )


BASE_MAKE_PARSER = ArgumentParser(
    add_help=False,
    parents=[LegacyDaemonCommand.PARSER],
)
BASE_MAKE_PARSER.add_argument(
    "--language",
    choices=["Python", "C++", "C", "Java", "Go", "Bash"],
    default="C++",
    help="which language to generate",
)
BASE_MAKE_PARSER.set_defaults(Command=LegacyDaemonCommand)

MAKE_PARSER = ArgumentParser(
    description="Generate all the necessary files for a problem",
    add_help=False,
    parents=[BASE_MAKE_PARSER],
)
MAKE_PARSER.add_argument(
    "what",
    choices=["skeleton", "template", "metadata", "description"],
    default="all",
    help="what to make",
)
