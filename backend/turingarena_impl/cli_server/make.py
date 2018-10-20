import json
import logging
import os
import sys
from contextlib import ExitStack

from turingarena_impl.cli_server.pack import create_working_directory
from turingarena_impl.driver.interface.interface import InterfaceDefinition
from turingarena_impl.driver.interface.metadata import generate_interface_metadata
from turingarena_impl.driver.language import Language

logger = logging.getLogger(__name__)


def make_cmd(args, local_execution):
    with ExitStack() as stack:
        work_dir = stack.enter_context(create_working_directory(
            args.working_directory,
            local_execution=local_execution,
        ))

        os.chdir(os.path.join(work_dir, args.working_directory.current_directory))

        language = Language.from_name(args.language)

        logger.info("Compiling interface")
        with open("interface.txt") as f:
            interface = InterfaceDefinition.compile(f.read())

        for message in interface.validate():
            logger.warning(f"{message}")

        if args.what == "skeleton":
            language.skeleton_generator().generate_to_file(interface, sys.stdout)
        if args.what == "template":
            language.template_generator().generate_to_file(interface, sys.stdout)
        if args.what == "description":
            for line in interface.main_node.node_description:
                print(line)
        if args.what == "metadata":
            json.dump(generate_interface_metadata(interface), sys.stdout, indent=4)

