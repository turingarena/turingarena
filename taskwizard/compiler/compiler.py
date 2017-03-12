"""Task Compiler.

Usage:
  taskcc makefile [-i <ifile>] [-o <ofile>]
  taskcc (stub|support|header) (interface <name>|driver) [-i <ifile>] [-o <ofile>]
  taskcc -h | --help

Options:
  -h --help          Show this screen.
  --version          Show version.
  name               The name of the interface/driver to use.
  -i --input=ifile   Path to task file [default: task.txt].
  -o --output=ofile  Path to output file.
"""

from docopt import docopt
from jinja2 import Environment, PackageLoader
import os
import sys

from taskwizard.compiler.grammar import GrammarParser
from taskwizard.compiler.semantics import Semantics


def main():
    args = docopt(__doc__)

    parse = GrammarParser(semantics=Semantics())
    text = open(args["--input"]).read()
    task = parse.parse(text)

    env = Environment(loader=PackageLoader("taskwizard.compiler", "templates"))

    if args["makefile"]:
        template = env.get_template("Makefile.j2")
    else:
        interface_or_driver = next(x for x in ["interface", "driver"] if args[x])
        if args["stub"]:
            template = env.get_template(os.path.join(interface_or_driver, "stub.cpp.j2"))
        elif args["header"]:
            template = env.get_template(os.path.join(interface_or_driver, "header.h.j2"))
        elif args["support"]:
            template = env.get_template(os.path.join(interface_or_driver, "support.cpp.j2"))
        else:
            raise ValueError

    output = sys.stdout
    if args["--output"] is not None:
        output = open(args["--output"], "w")

    if args["interface"]:
        template.stream(interface=task.interfaces[args["<name>"]]).dump(output)
    else:
        template.stream(task=task).dump(output)

    if args["--output"] is not None:
        output.close()
