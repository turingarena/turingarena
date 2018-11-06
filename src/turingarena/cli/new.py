import os
from argparse import ArgumentParser

from turingarena.cli.command import Command
from turingarena.cli.base import BASE_PARSER

evaluator_template = """\
import turingarena as ta

# insert here your evaluator code
"""

interface_template = """\
// constant declarations

// method declarations

main {

}    
"""


class NewCommand(Command):
    def run(self):
        name = self.args.name
        dirname = name.lower().replace(" ", "_")

        try:
            os.makedirs(dirname)
        except FileExistsError:
            print("Directory {}/ already exists in this directory!".format(dirname))
            exit(1)

        with open(os.path.join(dirname, "interface.txt"), "w") as f:
            print(interface_template, file=f)

        with open(os.path.join(dirname, "evaluator.py"), "w") as f:
            print(evaluator_template, file=f)

        os.makedirs(os.path.join(dirname, "solutions/"))
        print("Problem {} created in directory {}".format(name, dirname))

    PARSER = ArgumentParser(
        description="Create a new Turingarena problem",
        add_help=False,
        parents=[BASE_PARSER]
    )
    PARSER.add_argument("name", help="problem name")


NewCommand.PARSER.set_defaults(Command=NewCommand)
