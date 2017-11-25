import logging
import os
import shutil

from turingarena.sandbox.compile.cpp import compile_cpp

logger = logging.getLogger(__name__)


def compile(*, language, source_filename, protocol_name, interface_name, algorithm_name):
    if language is None:
        lang_by_extensions = {
            "cpp": "c++",
        }
        source_extension = source_filename.split(".")[-1]
        if source_extension not in lang_by_extensions:
            raise ValueError("unable to determine language from file extension")
        language = lang_by_extensions[source_extension]

    if algorithm_name is None:
        if interface_name is None:
            raise ValueError("please provide an algorithm name when no interface is used")
        algorithm_name = interface_name

    compilers = {
        "c++": compile_cpp
    }
    if language not in compilers:
        raise ValueError("unsupported language: {}".format(language))
    compiler = compilers[language]

    algorithm_dir = "algorithms/{}/".format(algorithm_name)

    logger.info(
        f"Compiling algorithm '{algorithm_name}'"
        f" with language {language} and source file '{source_filename}'"
    )

    logger.debug(f"Creating empty algorithm directory '{algorithm_dir}'")
    # cleanup
    os.makedirs(algorithm_dir, exist_ok=True)
    shutil.rmtree(algorithm_dir)

    os.mkdir(algorithm_dir)

    logger.debug("Creating language.txt file")
    with open(f"{algorithm_dir}/language.txt", "w") as language_file:
        print(language, file=language_file)

    logger.debug("Starting language-specific compilation")
    compiler(
        algorithm_dir=algorithm_dir,
        source_filename=source_filename,
        protocol_name=protocol_name,
        interface_name=interface_name,
    )
