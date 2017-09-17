"""TuringArena interface generator.

Parse and compiles an interface definition file,
and generates interface code for the supported languages.

Usage:
  turingarenagen [options] [<interfaces-file>] [-o <output-dir>]
  turingarenagen (-h | --help)

Options:

  <interfaces-file>  File containing the interface definition [default: interfaces.txt].
  -o --output-dir=<output-dir>  Directory where to generate code [default: ./generated]
  -h --help  Show this screen

"""

import docopt

from turingarena.interfaces import parser
from turingarena.interfaces.analysis.analysis import TaskAnalyzer
from turingarena.interfaces.generator import CodeGenerator


def main():
    args = docopt.docopt(__doc__)

    interface_file = args["<interfaces-file>"]
    task = parser.parse(open(interface_file).read(), rule="unit")

    TaskAnalyzer().analyze(task)
    CodeGenerator(task=task, output_dir=args["--output-dir"]).generate()


if __name__ == '__main__':
    main()
