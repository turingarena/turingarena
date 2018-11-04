from argparse import ArgumentParser

from turingarena_cli.remote import RemotePythonCommand
from turingarena_common.commands import InfoCommandParameters


class InfoCommand(RemotePythonCommand):
    def _get_command_parameters(self):
        return InfoCommandParameters(
            what=self.args.what,
        )

    PARSER = ArgumentParser(
        description="Get information about TuringArena",
        add_help=False,
        parents=[RemotePythonCommand.PARSER]
    )
    PARSER.add_argument("what", choices=["languages"], help="what info to get")


InfoCommand.PARSER.set_defaults(Command=InfoCommand)
