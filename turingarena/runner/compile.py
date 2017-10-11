"""TuringArena algorithm compiler.

Usage:
  turingarenac (-I <interface> | --no-interface) [-x <language>] [-o <name>] <source>
  turingarenac (-h | --help)

Options:

  <source>  Source file of the algorithm
  -I --interface=<interface>  Name of the interface this algorithm implements
  --no-interface  This algorithm handles stdin/stdout directly
  -x --language=<lang>  Language in which the algorithm is written
  -o --algorithm=<name>  Name of the algorithm to generate
  --log-level=<level>  Set logging level.

"""
import os
import shutil
from tempfile import TemporaryDirectory

import docopt

from turingarena.loggerinit import init_logger
from turingarena.runner.cpp import compile_cpp


import logging
logger = logging.getLogger(__name__)


def compile(source_filename, language=None, interface=None, algorithm_name=None):
    if language is None:
        lang_by_extensions = {
            "cpp": "cpp"
        }
        source_extension = source_filename.split(".")[-1]
        if source_extension not in lang_by_extensions:
            raise ValueError("unable to determine language from file extension")
        language = lang_by_extensions[source_extension]

    if algorithm_name is None:
        if interface is None:
            raise ValueError("please provide an algorithm name when no interface is used")
        algorithm_name = interface

    compilers = {
        "cpp": compile_cpp
    }
    if language not in compilers:
        raise ValueError("unsupported language: {}".format(language))
    compiler = compilers[language]

    algorithm_dir = "algorithms/{}/".format(algorithm_name)

    logger.info("Compiling algorithm '{algo}' with language {lang} and source file '{source}'".format(
        algo=algorithm_name,
        lang=language,
        source=source_filename,
    ))

    logger.debug("Creating empty algorithm directory '{}'".format(algorithm_dir))
    # cleanup
    os.makedirs(algorithm_dir, exist_ok=True)
    shutil.rmtree(algorithm_dir)

    os.mkdir(algorithm_dir)

    logger.debug("Creating language.txt file")
    with open("{}/language.txt".format(algorithm_dir), "w") as language_file:
        print(language, file=language_file)
    with open(source_filename) as source_file:
        logger.debug("Starting language-specific compilation")
        compiler(
            algorithm_dir=algorithm_dir,
            source_file=source_file,
            interface=interface,
        )


def main():
    args = docopt.docopt(__doc__)

    init_logger(args)

    compile(
        source_filename=args["<source>"],
        language=args["--language"],
        interface=args["--interface"],
        algorithm_name=args["--algorithm"],
    )

if __name__ == '__main__':
    main()
