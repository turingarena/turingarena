"""TuringArena algorithm compiler.

Usage:
  compile [options] <source>

Options:

  <source>  Source file of the algorithm
  -I --interface=<interface>  Name of the interface this algorithm implements
  -p --protocol=<interface>  Name of the protocol there the interface is defined
  -x --language=<lang>  Language in which the algorithm is written
  -o --algorithm=<name>  Name of the algorithm to generate

"""
import docopt

from turingarena.sandbox.compile import compile


def sandbox_compile_cli(argv):
    args = docopt.docopt(__doc__, argv=argv)

    compile(
        source_filename=args["<source>"],
        language=args["--language"],
        protocol_name=args["--protocol"],
        interface_name=args["--interface"],
        algorithm_name=args["--algorithm"],
    )
