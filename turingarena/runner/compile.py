"""TuringArena algorithm compiler.

Usage:
  turingarenac (-I <interface> | --no-interface) [-x <language>] [-o <name>] <source>
  turingarenac (-h | --help)

Options:

  -I --interface=<interface>  Name of the interface this algorithm implements
  --no-interface  This algorithm handles stdin/stdout directly
  -x --language=<lang>  Language in which the algorithm is written
  -o --algorithm=<name>  Name of the algorithm to generate
  <source>  Source file of the algorithm

"""
import os
import shutil
from tempfile import TemporaryDirectory

import docopt

from turingarena.runner.cpp import compile_cpp


def main():
    args = docopt.docopt(__doc__)

    interface = args["--interface"]
    lang = args["--language"]
    algorithm_name = args["--algorithm"]
    source_filename = args["<source>"]

    if algorithm_name is None:
        algorithm_name = interface
    if lang is None:
        lang_by_extensions = {
            "cpp": "cpp"
        }
        source_extension = source_filename.split(".")[-1]
        if source_extension not in lang_by_extensions:
            raise ValueError("unable to determine language from file extension")
        lang = lang_by_extensions[source_extension]

    compilers = {
        "cpp": compile_cpp
    }
    if lang not in compilers:
        raise ValueError("unsupported language: {}".format(lang))
    compiler = compilers[lang]

    algorithm_dir = "algorithms/{}/".format(algorithm_name)

    # cleanup
    os.makedirs(algorithm_dir, exist_ok=True)
    shutil.rmtree(algorithm_dir)

    os.mkdir(algorithm_dir)

    with open("{}/language.txt".format(algorithm_dir), "w") as language_file:
        print(lang, file=language_file)
    with open(source_filename) as source_file:
        compiler(
            algorithm_dir=algorithm_dir,
            source_file=source_file,
            interface=interface,
        )


if __name__ == '__main__':
    main()
