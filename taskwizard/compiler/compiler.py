"""Task Compiler.

Usage:
  taskcc (stub|support) (algorithm|driver) <name> [-i <ifile>] [-o <ofile>]
  taskcc -h | --help

Options:
  -h --help          Show this screen.
  --version          Show version.
  name               The name of the algorithm/driver to use.
  -i --input=ifile   Path to interface file.
  -o --output=ofile  Path to output file.
"""

import pkg_resources

from docopt import docopt

from taskwizard.compiler.grammar import GrammarParser
from taskwizard.compiler.semantics import Semantics


def main():
    args = docopt(__doc__)
    print(args)

    parse = GrammarParser(semantics=Semantics())
    text = open(args["<name>"]).read()
    algorithm = parse.parse(text)

    template = pkg_resources.resource_filename("taskwizard", "templates/stub_template.cpp.jinja2")
    stub_template_text = open(template).read()
    stub_template = Template(stub_template_text)

    open("tests/test_stub.cpp", "w").write(stub_template.render(algorithm=algorithm))

    template = pkg_resources.resource_filename("taskwizard", "templates/support_template.cpp.jinja2")
    support_template_text = open(template).read()
    support_template = Template(support_template_text)

    open("tests/test_support.cpp", "w").write(support_template.render(algorithm=algorithm))

    template = pkg_resources.resource_filename("taskwizard", "templates/support_template.cpp.jinja2")
    proto_template_text = open(template).read()
    proto_template = Template(proto_template_text)

    open("tests/test_proto.cpp", "w").write(proto_template.render(algorithm=algorithm))

