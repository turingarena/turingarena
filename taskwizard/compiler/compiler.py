"""Task Compiler.

Usage:
  taskcc (stub|support) (algorithm|driver) <name> [-i <ifile>] [-o <ofile>]
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
    algorithm = parse.parse(text)

    env = Environment(loader=PackageLoader("taskwizard", "templates"))

    stub_or_support = next(x for x in ["stub", "support"] if args[x])
    algorithm_or_driver = next(x for x in ["algorithm", "driver"] if args[x])
    template = env.get_template(stub_or_support + "_" + algorithm_or_driver + ".cpp.jinja2")

    output = sys.stdout
    if args["--output"] is not None:
        output = open(args["--output"], "w")

    template.stream(algorithm=algorithm).dump(output)

    if args["--output"] is not None:
        output.close()
