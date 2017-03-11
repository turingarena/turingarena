"""Task Compiler.

Usage:
  taskcc makefile [-i <ifile>] [-o <ofile>]
  taskcc (stub|support|header) (algorithm <name>|driver) [-i <ifile>] [-o <ofile>]
  taskcc -h | --help

Options:
  -h --help          Show this screen.
  --version          Show version.
  name               The name of the algorithm/driver to use.
  -i --input=ifile   Path to interface file [default: task.txt].
  -o --output=ofile  Path to output file.
"""

from docopt import docopt
from jinja2 import Environment, PackageLoader
import sys

from taskwizard.compiler.grammar import GrammarParser
from taskwizard.compiler.semantics import Semantics


def main():
    args = docopt(__doc__)

    parse = GrammarParser(semantics=Semantics())
    text = open(args["--input"]).read()
    interface = parse.parse(text)

    env = Environment(loader=PackageLoader("taskwizard", "templates"))

    if args["makefile"]:
        template = env.get_template("Makefile.jinja2")
    else:
        algorithm_or_driver = next(x for x in ["algorithm", "driver"] if args[x])
        if args["stub"]:
            template = env.get_template("stub_" + algorithm_or_driver + ".cpp.jinja2")
        elif args["header"]:
            template = env.get_template("header_" + algorithm_or_driver + ".h.jinja2")
        elif args["support"]:
            template = env.get_template("support_" + algorithm_or_driver + ".cpp.jinja2")
        else:
            raise ValueError

    output = sys.stdout
    if args["--output"] is not None:
        output = open(args["--output"], "w")

    if args["algorithm"]:
        template.stream(algorithm=interface.algorithms[args["<name>"]]).dump(output)
    else:
        template.stream(interface=interface).dump(output)

    if args["--output"] is not None:
        output.close()
