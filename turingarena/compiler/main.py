"""TuringArena interface compiler.

Compiles an interface definition file into code for the supported languages.

Usage:
  turingarenac [options] [<interface-file>] [-o <output-dir>]
  turingarenac (-h | --help)

Options:

  <interface-file>  File containing the interface definition
  -o --output-dir=<output-dir>  Directory where to generate code [default: ./generated]
  -h --help  Show this screen

"""

import docopt

from turingarena.compiler import parser
from turingarena.compiler.analysis.analysis import TaskAnalyzer
from turingarena.compiler.generator import CodeGenerator


def main():
    args = docopt.docopt(__doc__)

    interface_file = args["<interface-file>"] or "interfaces.txt"
    task = parser.parse(open(interface_file).read(), rule="unit")

    TaskAnalyzer().analyze(task)
    CodeGenerator(task=task, output_dir=args["--output-dir"]).generate()


if __name__ == '__main__':
    main()
