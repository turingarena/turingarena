from abc import abstractmethod, ABC


class Command(ABC):
    def __init__(self, args, cwd):
        self.args = args
        self.cwd = cwd

    @abstractmethod
    def run(self):
        pass


def add_subparser(subparsers, command):
    subparsers.add_parser(
        command.NAME,
        parents=[command.PARSER],
        help=command.PARSER.description,
    ).set_defaults(Command=command)
