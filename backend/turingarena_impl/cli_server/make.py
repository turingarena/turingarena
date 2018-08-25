import json
import logging
import os
import sys
from contextlib import contextmanager

from turingarena_impl.cli_server.git_manager import add_directory, commit_work
from turingarena_impl.driver.interface.interface import InterfaceDefinition
from turingarena_impl.driver.interface.metadata import generate_interface_metadata
from turingarena_impl.driver.language import Language

logger = logging.getLogger(__name__)


@contextmanager
def generate(directory, filename):
    if directory is None:
        yield sys.stdout
    else:
        file = os.path.join(directory, filename)
        logger.info(f"Generating {file}")
        with open(file, "w") as f:
            try:
                yield f
            except:
                logging.exception(f"Exception during {filename} generation")


def make_skeleton(out_dir, interface, language):
    with generate(out_dir, f"skeleton{language.extension}") as out:
        language.skeleton_generator().generate_to_file(interface, out)


def make_template(out_dir, interface, language):
    with generate(out_dir, f"template{language.extension}") as out:
        language.template_generator().generate_to_file(interface, out)


def make_metadata(out_dir, interface):
    with generate(out_dir, f"metadata.json") as out:
        json.dump(generate_interface_metadata(interface), out, indent=4)


def make_description(out_dir, interface):
    with generate(out_dir, f"metadata.json") as out:
        for line in interface.main_node.node_description:
            print(line, file=out)


def make(directory, what, languages, file_output=False):
    out_dir = None
    if file_output:
        out_dir = os.path.join(directory, "__turingarena_make_output__")
        os.makedirs(out_dir, exist_ok=True)

    logger.info(f"Entering directory {directory}")

    interface_file = os.path.join(directory, "interface.txt")

    with open(interface_file) as f:
        interface_text = f.read()

    logger.info("Compiling interface")

    interface = InterfaceDefinition.compile(interface_text)

    for message in interface.validate():
        logger.warning(f"{message}")

    for language in languages:
        language_dir = None
        if out_dir:
            language_dir = os.path.join(out_dir, language.name)
            os.makedirs(language_dir, exist_ok=True)

        if "skeleton" in what:
            make_skeleton(out_dir=language_dir, interface=interface, language=language)
        if "template" in what:
            make_template(out_dir=language_dir, interface=interface, language=language)

    if "description" in what:
        make_description(out_dir=out_dir, interface=interface)

    if "metadata" in what:
        make_metadata(out_dir=out_dir, interface=interface)

    if not print:
        add_directory(out_dir)


def make_cmd(args):
    what = args.what

    if what == "all":
        what = ["skeleton", "template", "metadata"]
    else:
        what = [what]

    languages = []
    if args.language:
        for language in args.language:
            try:
                languages.append(Language.from_name(language))
            except ValueError:
                logging.error(f"Language {language} not supported")
    elif what == "all":
        languages = Language.languages()
    else:
        languages = [Language.from_name("c++")]

    base_dir = os.getcwd()
    logger.info(f"Searching for problems in {base_dir}")
    for subdir, dir, files in os.walk(base_dir):
        if "interface.txt" in files:
            make(directory=subdir, what=what, languages=languages, file_output=not args.print)

    if not args.print:
        tree_id, commit_id = commit_work()
        result = dict(tree_id=tree_id, commit_id=commit_id)
        logger.info(f"Writing result to file {args.result_file}")
        with open(args["result_file"], "w") as f:
            print(json.dumps(result), file=f)
