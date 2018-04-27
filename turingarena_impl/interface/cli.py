import sys

from turingarena_impl.cli import docopt_cli
from turingarena_impl.interface.interface import InterfaceDefinition
from turingarena_impl.sandbox.languages.language import Language


@docopt_cli
def generate_template_cli(args):
    """Generate interface template code.

    Usage:
        template [options]

    Options:
        -x --language=<lang>  Source language [default: c++].
        -I --interface=<file>  Interface definition file [default: interface.txt].
    """

    with open(args["--interface"]) as f:
        interface_text = f.read()

    interface = InterfaceDefinition.compile(interface_text)
    language = Language.from_name(args["--language"])
    generator = language.template_generator(interface)
    generator.write_to_file(sys.stdout)


@docopt_cli
def generate_skeleton_cli(args):
    """Generate interface skeleton code (for debugging).

    Usage:
        skeleton [options]

    Options:
        -x --language=<lang>  Source language [default: c++].
        -I --interface=<file>  Interface definition file [default: interface.txt].
    """

    with open(args["--interface"]) as f:
        interface_text = f.read()

    interface = InterfaceDefinition.compile(interface_text)
    language = Language.from_name(args["--language"])
    generator = language.skeleton_generator(interface)
    generator.write_to_file(sys.stdout)


@docopt_cli
def validate_interface_cli(args):
    """Validate interface file

    Usage:
        validate [options]

    Options:
        -I --interface=<file>  Interface definition file [default: interface.txt].
    """

    with open(args["--interface"]) as f:
        interface_text = f.read()

    interface = InterfaceDefinition.compile(interface_text, validate=False)

    for message in interface.validate():
        print(message)
