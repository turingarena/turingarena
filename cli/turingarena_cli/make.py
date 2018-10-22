import sys
from argparse import ArgumentParser

from turingarena_cli.pack import PackBasedCommand
from turingarena_cli.remote import RemotePythonCommand
from turingarena_common.commands import MakeCommandParameters


class LegacyCommand(PackBasedCommand, RemotePythonCommand):
    def _get_command_parameters(self):
        return MakeCommandParameters(
            what=self.args.what,
            language=self.args.language,
            working_directory=self.working_directory,
        )

    PARSER = ArgumentParser(
        add_help=False,
        parents=[PackBasedCommand.PARSER],
        description="Generate problem file",
    )
    PARSER.add_argument(
        "--language",
        choices=["Python", "C++", "C", "Java", "Go", "Bash"],
        default="C++",
        help="which language to generate",
    )


class LegacyMakeCommand(LegacyCommand):
    def run(self):
        print(f"WARNING: The command 'turingarena make' is deprecated and will be removed in the future.", file=sys.stderr)
        print("Use the new command 'turingarena file cat' instead", file=sys.stderr)

        super(LegacyCommand, self).run()

    PARSER = ArgumentParser(
        add_help=False,
        parents=[LegacyCommand.PARSER],
        description="Generate a problem file"
    )
    PARSER.add_argument(
        "what",
        choices=["skeleton", "template", "metadata", "description"],
        help="what to generate",
    )


LegacyMakeCommand.PARSER.set_defaults(Command=LegacyMakeCommand)


class LegacySkeletonCommand(LegacyCommand):
    PARSER = ArgumentParser(
        add_help=False,
        parents=[LegacyCommand.PARSER],
        description="Generate skeleton"
    )

    def run(self):
        print(f"WARNING: The command 'turingarena skeleton' is deprecated and will be removed in the future.", file=sys.stderr)
        print("Use the new command 'turingarena file cat' instead", file=sys.stderr)
        self.args.what = "skeleton"

        super(LegacyCommand, self).run()


LegacySkeletonCommand.PARSER.set_defaults(Command=LegacySkeletonCommand)


class LegacyTemplateCommand(LegacyCommand):
    PARSER = ArgumentParser(
        add_help=False,
        parents=[LegacyCommand.PARSER],
        description="Generate template"
    )

    def run(self):
        print(f"WARNING: The command 'turingarena template' is deprecated and will be removed in the future.", file=sys.stderr)
        print("Use the new command 'turingarena file cat' instead", file=sys.stderr)
        self.args.what = "template"

        super(LegacyCommand, self).run()


LegacyTemplateCommand.PARSER.set_defaults(Command=LegacyTemplateCommand)